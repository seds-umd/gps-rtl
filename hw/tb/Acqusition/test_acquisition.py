import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotbext import axi

import numpy as np
import logging
from gps import gps_sim

import sys
from pathlib import Path

# Hack to share fft_sim between multiple tests
fft_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(fft_path.resolve()))

from fft_sim import FFT_Sim, pack_complex, unpack_complex

async def feed_iq(dut, fs):
    # Set up AXI interface
    bus = axi.AxiStreamBus(dut)
    bus._add_signal("tdata", "io_iq_payload")
    bus._add_signal("tvalid", "io_iq_valid")
    bus._add_signal("tready", "io_iq_ready")
    iq_bus = axi.AxiStreamSource(bus, dut.clk, byte_size=4)
    iq_bus.log.setLevel(logging.WARNING) # Get rid of log messages

    # samples = 127 * gps_sim.generate_gps(fs, int(fs*0.1), 1, fs/4096, code_phase=500, signal_power=-130)
    samples = 127 * gps_sim.generate_gps(fs, int(fs*0.1), 1, fs/4096, code_phase=0, signal_power=None)
    samples_re = samples.real.astype(np.int8).astype(np.uint8) >> 6
    samples_im = samples.imag.astype(np.int8).astype(np.uint8) >> 6
    bits = samples_re | (samples_im << 2)
    bits = [int(x) for x in bits]

    iq_bus.send_nowait(bits)
    await iq_bus.wait()

@cocotb.test()
async def test_acquisition(dut, fs=4.092e6):
    cocotb.start_soon(Clock(dut.clk, 20, "ns").start()) # 50 MHz
    cocotb.start_soon(feed_iq(dut, fs))

    sim = FFT_Sim(dut.fft_inst, 12, 1)

    dut.reset.value = 0
    await ClockCycles(dut.clk, 2)
    dut.reset.value = 1
    await ClockCycles(dut.clk, 2)
    dut.reset.value = 0

    await ClockCycles(dut.clk, 60000)
