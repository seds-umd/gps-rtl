import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, with_timeout
from cocotbext import axi

import random
import logging
import numpy as np

def randbytes(n, b=8):
    for _ in range(n):
        yield random.getrandbits(b)

@cocotb.test()
async def test_interface(dut, N=1024):
    assert N % 16 == 0, "N must be a multiple of 16"

    dut.io_rst.value = 1

    # Generate random IQ samples
    bits_per_half_sample = 2
    # Samples formatted as [[[I0, I1], [Q0, Q1]]]*N
    samples = [[[random.getrandbits(1) for _ in range(bits_per_half_sample)] for _ in range(2)] for _ in range(N)]
    samples = np.array(samples)
    samples_ref = samples[:, :, 0] + 2*samples[:, :, 1]

    # Set up clocks
    cocotb.start_soon(Clock(dut.io_clk, period=20, units="ns").start())
    cocotb.start_soon(Clock(dut.io_clk_ser, period=125, units="ns").start())

    await RisingEdge(dut.io_clk)
    dut.io_rst.value = 0
    await RisingEdge(dut.io_clk_ser)

    # Set up AXI interface
    axi_bus = axi.AxiStreamBus(dut)
    axi_bus._add_signal("tdata", "io_iq_payload")
    axi_bus._add_signal("tvalid", "io_iq_valid")
    axi_bus._add_signal("tready", "io_iq_ready")
    axi_output = axi.AxiStreamSink(axi_bus, dut.io_clk, dut.io_rst, byte_size=1)
    axi_output.log.setLevel(logging.WARNING) # Get rid of log messages

    samples_recv = []

    # Send IQ samples
    for i in range(0, N, 16):
        block = samples[i:i+16]

        # I1, I0, Q1, Q0
        for idx in [(0, 1), [0, 0], [1, 1], [1, 0]]:
            for j in range(16):
                dut.io_data_in.value = int(block[j, idx[0], idx[1]])

                if j == 0:
                    dut.io_data_sync.value = 1
                else:
                    dut.io_data_sync.value = 0

                await RisingEdge(dut.io_clk_ser)

            # Add variable delay
            if (i // 16) % 4 == idx[0] + 2*idx[1]:
                await ClockCycles(dut.io_clk_ser, (i // 16) % 16)

    for j in range(N):
        frame = await with_timeout(axi_output.recv(), 125*64, "ns")
        samples_recv.append(frame.tdata)

    samples_recv = np.array([[x[0]+2*x[1], x[2]+2*x[3]] for x in samples_recv])

    matched = samples_recv - samples_ref == 0
    wrong = int(np.argmin(matched, axis=0)[0])

    assert matched.all(), f"{wrong}, {samples_recv[wrong]}, {samples_ref[wrong]}"
