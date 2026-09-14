"""Paced MAX serial pins through acquisition; synthetic RF and vendor FFT model."""
import logging

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, RisingEdge, with_timeout
import numpy as np

import fpga_utils
from fpga_utils import test_runner
from fpga_utils.fft_sim import FFT_Sim
from fpga_utils.spinal_stream import SpinalStreamSink


async def send_serial(dut, packed):
    # Each block is I-MSB, I-LSB, Q-MSB, Q-LSB,16 samples per plane.
    for start in range(0, len(packed), 16):
        for bit in [1, 0, 3, 2]:
            for j, sample in enumerate(packed[start:start + 16]):
                await FallingEdge(dut.io_clk_ser)
                dut.io_data_sync.value = int(j == 0)
                dut.io_data_in.value = (sample >> bit) & 1
                await RisingEdge(dut.io_clk_ser)
    await FallingEdge(dut.io_clk_ser)
    dut.io_data_sync.value = 0


async def check_coarse_windows(dut):
    count, previous = 0, None
    while True:
        await RisingEdge(dut.clk)
        if int(dut.reset.value):
            continue
        gate = dut.acq.fft_in_gate
        if int(dut.acq.fft_input_sel.value) == 0 and int(gate.io_output_valid.value) and int(gate.io_output_ready.value):
            timestamp = int(dut.acq.io_iq_payload.value) >> 4
            if count % 4096 == 0:
                dut._log.info(f"Coarse window {count // 4096 + 1} begins at timestamp {timestamp}")
            else:
                assert timestamp == (previous + 1) % 4092, f"Coarse sample gap at index{count % 4096}: {previous} -> {timestamp}"
            previous = timestamp
            count += 1


async def check_fine_windows(dut, counts):
    previous = None
    fine = dut.acq.fine_acq_remove_prn
    while True:
        await RisingEdge(dut.clk)
        if int(dut.reset.value) or not int(fine.aligned.value):
            previous = None
            continue
        if int(fine.io_input_valid.value) and int(fine.io_input_ready.value):
            timestamp = int(fine.io_input_payload_t.value)
            if previous is None:
                counts.append(0)
            else:
                assert timestamp == (previous + 1) % 4092, f"Fine sample gap: {previous} -> {timestamp}"
            counts[-1] += 1
            previous = timestamp


@cocotb.test(timeout_time=30, timeout_unit="ms")
async def serial_input_finds_second_satellite(dut):
    dut.reset.value = 1
    dut.io_data_sync.value = 0
    dut.io_time_sync.value = 0
    dut.io_data_in.value = 0
    cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())
    cocotb.start_soon(Clock(dut.io_clk_ser, 61, units="ns").start())
    fft = FFT_Sim(dut.acq.fft_inst, 12, 1, store=False)
    fft.log.setLevel(logging.WARNING)
    results = SpinalStreamSink.from_prefix(dut, "io_results")
    cocotb.start_soon(check_coarse_windows(dut))
    fine_counts = []
    cocotb.start_soon(check_fine_windows(dut, fine_counts))
    await ClockCycles(dut.io_clk_ser, 8)
    await FallingEdge(dut.clk)
    dut.reset.value = 0
    np.random.seed(20260914)
    packed, _, _ = fpga_utils.generate_gps_samples(4.092e6, 131072, 2, 4.092e6 / 4096, 37, None)
    sender = cocotb.start_soon(send_serial(dut, packed))
    first_metric = None
    for expected_sv in [1, 2]:
        frame = await with_timeout(results.read(), 15, "ms")
        values = {key: value[0] for key, value in frame.payload.items()}
        if values["freq_offset"] >= 2048:
            values["freq_offset"] -= 4096
        dut._log.info(f"Serial acquisition result: {values}")
        assert values["sv"] == expected_sv
        if expected_sv == 1:
            # Results enumerate every PRN; there is no hardware detection flag.
            # A wrong PRN can still exceed the old host's uncalibrated8 cutoff.
            first_metric = values["snr"]
        else:
            assert values["snr"] > 8
            assert values["snr"] > 4 * first_metric
            assert abs(values["freq_offset"] - 8) <= 1
            error = (values["phase_offset"] - 37) % 4092
            assert min(error, 4092 - error) <= 1
    # The live-input adapter discards samples outside acquisition windows;
    # the serial FIFO itself must keep draining without overflow.
    assert int(dut.io_sample_overflow.value) == 0
    dut._log.info(f"Contiguous fine-window sample counts: {fine_counts}")
    assert len(fine_counts) == 2 and all(count >= 32768 for count in fine_counts)
    sender.kill()


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="GpsTopSim", scala_name="GpsTop", scala_object="GpsTopSimVerilog",
        test_module="test_gpstop", package="gps", proj_dir="../../..",
        source_dir="hw/spinal/gps", gen_dir="hw/gen",
        spinal_sources=["AcquisitionModular", "MaxInterface"],
        verilog_sources=["hw/verilog/XilinxFFT.v"],
    )
