import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotbext import axi

import numpy as np
import logging

from gps import gps_sim


# Calculate correlation between two signals, between 1 and -1
def corr(a: np.ndarray, b: np.ndarray):
    assert len(a) == len(b), f"Arrays must be the same length, {len(a)} != {len(b)}"

    a_norm = (a - np.mean(a)) / np.std(a)
    b_norm = (b - np.mean(b)) / np.std(b)

    return np.abs(np.sum(a_norm * b_norm.conjugate())) / len(a)


# Random pause generator for AXI bus
def random_pause():
    while True:
        yield np.random.choice([0, 1])


def stream_axis_bus(dut, prefix: str, fragment: bool = False, user: bool = False):
    axi_bus = axi.AxiStreamBus(dut)

    # Add signals to bus

    if fragment:
        # Janky way to handle different names for payload by seeing which one actually exists
        data_name = ""

        for element in dut:
            if element._name == prefix + "payload_fragment":
                data_name = "payload_fragment"

            if element._name == prefix + "payload_data":
                data_name = "payload_data"

        assert len(data_name) > 0

        axi_bus._add_signal("tdata", prefix + data_name)
        axi_bus._add_signal("tlast", prefix + "payload_last")
    else:
        axi_bus._add_signal("tdata", prefix + "payload")

    axi_bus._add_signal("tvalid", prefix + "valid")
    axi_bus._add_signal("tready", prefix + "ready")

    if user:
        axi_bus._add_signal("tuser", prefix + "payload_user")

    return axi_bus


def axis_sink(dut, prefix: str, fragment: bool = False, user: bool = False, **kwargs):
    bus = stream_axis_bus(dut, prefix, fragment, user)
    sink = axi.AxiStreamSink(bus, dut.clk, dut.reset, **kwargs)
    sink.log.setLevel(logging.WARNING)

    return sink


def axis_source(dut, prefix: str, fragment: bool = False, user: bool = False, **kwargs):
    bus = stream_axis_bus(dut, prefix, fragment, user)
    source = axi.AxiStreamSource(bus, dut.clk, dut.reset, **kwargs)
    source.log.setLevel(logging.WARNING)

    return source


def pack_iq(samples: np.ndarray):
    samples /= np.max([samples.real, samples.imag])
    samples *= 127 * 3 / 4

    samples_re = samples.real.astype(np.int8).astype(np.uint8) >> 6
    samples_im = samples.imag.astype(np.int8).astype(np.uint8) >> 6
    bits = samples_re | (samples_im << 2)
    bits = [int(x) for x in bits]

    return bits

# Simulate sample rate
def iq_pause(f=50, fs=4.092):
    x = 0

    while True:
        x += 1 / f

        if x > 1 / fs:
            x -= 1 / fs
            yield False
        else:
            yield True


def generate_gps_samples(
    fs: float,
    count: int,
    sv: int,
    doppler: float,
    sample_phase: int,
    noise_power: float,
):
    """Generate GPS samples to send in IQ timestamp format.

    Args:
        fs (float): Sample rate in Hz
        count (int): Number of samples to generate
        sv (int): SV number (1 indexed)
        doppler (float): Doppler frequency shift
        sample_phase (int): Phase offset in number of samples
        noise_power (float): Noise power in dBm

    Returns:
        (list[int], np.ndarray, np.ndarray): Packed bits, original samples, quantized samples
    """

    # 3/4 is about optimal for 33% magnitude bit density (per MAX2769 datasheet)
    samples = (3 / 4 * 127) * gps_sim.generate_gps(
        f_s=fs,
        n=int(count),
        sv=sv,
        doppler=doppler,
        sample_phase=sample_phase,
        signal_power=noise_power,
    )
    timestamp = np.tile(np.arange(4092), int(len(samples) / 4092) + 1)
    timestamp = timestamp.astype(np.uint16)[0 : len(samples)]

    # Convert to 4 bit format
    samples_re = samples.real.astype(np.int8).astype(np.uint8) >> 6
    samples_im = samples.imag.astype(np.int8).astype(np.uint8) >> 6
    bits = samples_re | (samples_im << 2) | (timestamp << 4)
    bits = [int(x) for x in bits]

    # Get quantized samples
    samples_re = (samples_re << 6).astype(np.int8) | 0b100000
    samples_im = (samples_im << 6).astype(np.int8) | 0b100000

    samples_quant = samples_re + samples_im * 1j
    samples_quant /= 128

    return bits, samples, samples_quant


class TB_Template:
    def __init__(self, dut, period=10):
        self.dut = dut
        self.period = period

        cocotb.start_soon(Clock(self.dut.clk, period=period, units="ns").start())

    async def reset(self, delay=2):
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, delay)
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, delay)
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, delay)
