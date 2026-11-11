"""MAX2769 emulator through the real MaxInterface, checked against the Python model."""
from pathlib import Path
import sys

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge, with_timeout
import numpy as np

from fpga_utils import test_runner
from fpga_utils.spinal_stream import SpinalStreamSink
from gps.gps import acquisition, fine_acquisition

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import max_emulator as model  # noqa: E402

SERIAL_PERIOD_NS = 61  # 4 bits per sample at about 4.092 Msps
SYSTEM_PERIOD_NS = 20
CHANNELS = 2


def to_signed(values, bits=2):
    values = np.array(values, dtype=np.int64)
    values[values >= 1 << (bits - 1)] -= 1 << bits
    return values


async def collect_serial_samples(dut, store):
    """Record the emulator's pre-serializer samples in the serial domain."""
    while True:
        await RisingEdge(dut.io_clk_ser)
        if int(dut.io_sample_valid.value):
            store.append((int(dut.io_sample_payload_re.value), int(dut.io_sample_payload_im.value)))


def apply_config(dut, channels, noise_gain, threshold, seed):
    for k in range(CHANNELS):
        channel = channels[k] if k < len(channels) else model.Channel(sv=1, enable=False)
        prefix = f"io_config_channel_{k}_"
        getattr(dut, prefix + "enable").value = int(channel.enable)
        getattr(dut, prefix + "sv").value = channel.sv - 1
        getattr(dut, prefix + "code_phase").value = channel.code_phase
        getattr(dut, prefix + "carrier_inc").value = channel.carrier_inc & 0xFFFFFFFF
        getattr(dut, prefix + "amplitude").value = channel.amplitude
    dut.io_config_noise_gain.value = noise_gain
    dut.io_config_threshold.value = threshold
    dut.io_config_seed.value = seed & 0xFFFFFFFF


async def start(dut, channels, noise_gain=0, threshold=64, seed=0):
    """Reset the receiver and the emulator together, then start a fresh run."""
    await FallingEdge(dut.io_clk_ser)
    dut.io_run.value = 0
    await FallingEdge(dut.clk)
    dut.reset.value = 1
    apply_config(dut, channels, noise_gain, threshold, seed)
    await ClockCycles(dut.io_clk_ser, 8)
    await FallingEdge(dut.clk)
    dut.reset.value = 0
    await ClockCycles(dut.io_clk_ser, 4)
    await FallingEdge(dut.io_clk_ser)
    dut.io_run.value = 1


async def setup(dut):
    dut.reset.value = 1
    dut.io_run.value = 0
    dut.io_iq_ready.value = 1
    apply_config(dut, [], 0, 64, 0)
    cocotb.start_soon(Clock(dut.clk, SYSTEM_PERIOD_NS, units="ns").start())
    cocotb.start_soon(Clock(dut.io_clk_ser, SERIAL_PERIOD_NS, units="ns").start())
    await ClockCycles(dut.clk, 4)


async def receive(dut, sink, count):
    async def wait():
        while sink.count() < count:
            await ClockCycles(dut.clk, 64)

    # Four serial clocks per sample, plus start-up and code pre-roll.
    budget_ns = SERIAL_PERIOD_NS * (4 * count + 8192)
    await with_timeout(wait(), budget_ns, "ns")
    frame = sink.read_nowait(count)
    return (
        to_signed(frame.payload["c_re"]),
        to_signed(frame.payload["c_im"]),
        np.array(frame.payload["t"], dtype=np.int64),
    )


async def run_and_compare(dut, channels, count, noise_gain=0, threshold=64, seed=0):
    sink = SpinalStreamSink.from_prefix(dut, "io_iq")
    raw = []
    await start(dut, channels, noise_gain, threshold, seed)
    # Started after run rises, so no sample of an earlier run can be recorded.
    monitor = cocotb.start_soon(collect_serial_samples(dut, raw))
    i, q, t = await receive(dut, sink, count)
    monitor.kill()

    expected_i, expected_q = model.samples(channels, count, noise_gain, threshold, seed)
    # Sample 0 of the emulator must land on receiver timestamp 0.
    np.testing.assert_array_equal(t, np.arange(count) % model.PERIOD)
    np.testing.assert_array_equal(i, expected_i, err_msg="I samples differ from the model")
    np.testing.assert_array_equal(q, expected_q, err_msg="Q samples differ from the model")

    raw = np.array(raw[:count], dtype=np.int64)
    np.testing.assert_array_equal(to_signed(raw[:, 0]), expected_i[: len(raw)])
    np.testing.assert_array_equal(to_signed(raw[:, 1]), expected_q[: len(raw)])
    assert int(dut.io_overflow.value) == 0
    return i, q


@cocotb.test()
async def matches_model_two_satellites_with_noise(dut):
    """Two satellites plus noise: every sample and timestamp matches the model."""
    await setup(dut)
    channels = [
        model.Channel(sv=2, code_phase=37, carrier_inc=model.inc_for_fine_bin(8), amplitude=40),
        model.Channel(sv=25, code_phase=4091, carrier_inc=model.inc_for_fine_bin(-52) + 12345, amplitude=25),
    ]
    i, q = await run_and_compare(dut, channels, 6000, noise_gain=60, threshold=70, seed=0x5EED5EED)
    # The noise has to be doing something: all four levels appear on both rails.
    assert set(np.unique(i)) == {-2, -1, 0, 1} and set(np.unique(q)) == {-2, -1, 0, 1}


@cocotb.test()
async def restart_is_deterministic(dut):
    """A second run with a new configuration starts cleanly from sample 0."""
    await setup(dut)
    first = [model.Channel(sv=11, code_phase=5, carrier_inc=model.inc_for_fine_bin(3))]
    await run_and_compare(dut, first, 1024)
    second = [
        model.Channel(sv=1, enable=False),
        model.Channel(sv=32, code_phase=2047, carrier_inc=model.inc_for_fine_bin(-9), amplitude=200),
    ]
    await run_and_compare(dut, second, 1024, noise_gain=5, threshold=100, seed=7)


@cocotb.test()
async def restart_with_run_alone(dut):
    """GpsSelfTest restarts the emulator with run only, never its reset: the samples must still match."""
    await setup(dut)
    await run_and_compare(dut, [model.Channel(sv=4, code_phase=3000, carrier_inc=model.inc_for_fine_bin(77))], 600)

    channels = [
        model.Channel(sv=29, code_phase=1, carrier_inc=model.inc_for_fine_bin(-150), amplitude=70),
        model.Channel(sv=8, code_phase=4000, carrier_inc=model.inc_for_fine_bin(31), amplitude=50),
    ]
    # Stop in the middle of a 16-sample block, change everything, start again.
    await ClockCycles(dut.io_clk_ser, 37)
    await FallingEdge(dut.io_clk_ser)
    dut.io_run.value = 0
    await ClockCycles(dut.io_clk_ser, 5)
    apply_config(dut, channels, 33, 90, 0xABCDEF)
    await ClockCycles(dut.io_clk_ser, 3)
    await FallingEdge(dut.io_clk_ser)
    dut.io_run.value = 1
    raw = []
    monitor = cocotb.start_soon(collect_serial_samples(dut, raw))
    count = 700
    while len(raw) < count:
        await ClockCycles(dut.io_clk_ser, 256)
    monitor.kill()
    raw = np.array(raw[:count], dtype=np.int64)
    expected_i, expected_q = model.samples(channels, count, 33, 90, 0xABCDEF)
    np.testing.assert_array_equal(to_signed(raw[:, 0]), expected_i)
    np.testing.assert_array_equal(to_signed(raw[:, 1]), expected_q)


@cocotb.test()
async def reference_receiver_acquires_the_signal(dut):
    """The gps-model software receiver finds the programmed satellite, phase and Doppler."""
    await setup(dut)
    sv, code_phase, fine_bin = 7, 1000, 16
    channels = [model.Channel(sv=sv, code_phase=code_phase, carrier_inc=model.inc_for_fine_bin(fine_bin))]
    count = model.PERIOD * 9  # One period for coarse search plus 4096 * 8 for fine
    i, q = await run_and_compare(dut, channels, count)
    x = model.to_complex(i, q)

    detections = acquisition(x, model.SAMPLE_RATE, 24e3, 1000, 0, threshold=6)
    dut._log.info(f"Software acquisition: {detections}")
    assert [d[0] for d in detections] == [sv], "exactly the programmed satellite should be detected"
    _, coarse_hz, phase, _ = detections[0]
    assert int(phase) == code_phase
    assert abs(coarse_hz - channels[0].doppler_hz) < 500

    fine_hz, _ = fine_acquisition(x, model.SAMPLE_RATE, 4096, 8, sv, int(phase))
    assert abs(fine_hz / model.FINE_BIN_HZ - fine_bin) < 1e-6


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="MaxEmulatorLoopback", scala_name="MaxEmulator", scala_object="MaxEmulatorVerilog",
        test_module="test_maxemulator", package="gps", proj_dir="../../..",
        source_dir="hw/spinal/gps", gen_dir="hw/gen",
        spinal_sources=["MaxInterface", "PrnGenerator"],
    )
