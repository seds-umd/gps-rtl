import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import logging
import numpy as np

from fpga_utils import test_runner, stream_axis_bus


class TB:
    def __init__(self, dut, lanes=4):
        self.dut = dut
        self.lanes = lanes

        cocotb.start_soon(Clock(self.dut.clk, period=10, units="ns").start())

        in_buses = [
            stream_axis_bus(self.dut, f"io_inputs_{i}_") for i in range(self.lanes)
        ]
        self.axis_inputs = [
            axi.AxiStreamSource(bus, self.dut.clk, self.dut.reset) for bus in in_buses
        ]
        for axis in self.axis_inputs:
            axis.log.setLevel(logging.WARNING)

        out_bus = stream_axis_bus(self.dut, "io_output_")
        self.axis_output = axi.AxiStreamSink(out_bus, dut.clk, dut.reset)
        self.axis_output.log.setLevel(logging.WARNING)

    async def reset(self):
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 2)

    async def run_test(self, sel: int, n: int):
        assert sel < self.lanes, "Selection out of bounds"

        expected = np.random.bytes(n)

        self.axis_inputs[sel].send_nowait(expected)

        self.dut.io_sel.value = sel
        self.dut.io_run.value = 1
        await ClockCycles(self.dut.clk, 1)
        self.dut.io_run.value = 0
        await ClockCycles(self.dut.clk, 5)

        await with_timeout(self.axis_inputs[sel].idle_event.wait(), 1000, "ns")

        actual = self.axis_output.read_nowait(64)
        actual = bytes(actual)

        assert actual == expected


@cocotb.test()
async def test_streammuxmetered(dut):
    N = 8

    tb = TB(dut)
    await tb.reset()

    # Test runs
    for _ in range(100):
        sel = np.random.randint(4)
        await tb.run_test(sel, N)

if __name__ == "__main__":
    # test_runner.run_wrapper(
    #     top_level="StreamMuxMetered",
    #     package="gps",
    #     proj_dir="../../..",
    #     source_dir="hw/spinal/gps",
    #     gen_dir="hw/gen",
    # )
    print("StreamMuxMetered - Unused, skipping test")
