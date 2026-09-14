import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, with_timeout
from fpga_utils.spinal_stream import SpinalStreamSink

import random
import logging
import numpy as np

def randbytes(n, b=8):
    for _ in range(n):
        yield random.getrandbits(b)

@cocotb.test()
async def test_interface(dut, N=8192):
    assert N % 16 == 0, "N must be a multiple of 16"

    dut.reset.value = 1
    dut.io_time_sync.value = 0
    dut.io_data_sync.value = 0
    dut.io_data_in.value = 0

    # Generate random IQ samples
    bits_per_half_sample = 2
    # Samples formatted as [[[I0, I1], [Q0, Q1]]]*N
    samples = [[[random.getrandbits(1) for _ in range(bits_per_half_sample)] for _ in range(2)] for _ in range(N)]
    samples = np.array(samples)
    samples_ref = samples[:, :, 0] + 2*samples[:, :, 1]

    # Set up clocks
    cocotb.start_soon(Clock(dut.clk, period=20, units="ns").start())
    cocotb.start_soon(Clock(dut.io_clk_ser, period=125, units="ns").start())

    await RisingEdge(dut.clk)
    dut.reset.value = 0
    await RisingEdge(dut.io_clk_ser)

    # The receiver exposes a structured stream: I, Q and sample timestamp.
    output = SpinalStreamSink.from_prefix(dut, "io_iq")

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

    dut.io_data_sync.value = 0
    async def wait_for_samples():
        while output.count() < N:
            await ClockCycles(dut.clk, 16)

    await with_timeout(wait_for_samples(), 125 * 64 * (N // 16), "ns")
    frame = output.read_nowait(N)
    samples_recv = np.column_stack((frame.payload["c_re"], frame.payload["c_im"]))
    np.testing.assert_array_equal(frame.payload["t"], np.arange(N) % 4092)

    matched = samples_recv - samples_ref == 0
    wrong = int(np.argmin(matched, axis=0)[0])

    assert matched.all(), f"{wrong}, {samples_recv[wrong]}, {samples_ref[wrong]}"


from fpga_utils import test_runner

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level='MaxInterface',
        test_module='test_max_interface',
        package='gps',
        proj_dir='../../..',
        source_dir='hw/spinal/gps',
        gen_dir='hw/gen',
    )
