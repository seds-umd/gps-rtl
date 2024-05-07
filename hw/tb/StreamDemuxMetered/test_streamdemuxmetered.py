import cocotb
from cocotb.clock import Clock
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import logging
import numpy as np
import sys
from pathlib import Path

utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from utils import stream_axis_bus


class TB:
    def __init__(self, dut, lanes=4):
        self.dut = dut
        self.lanes = lanes

        cocotb.start_soon(Clock(self.dut.clk, period=10, units="ns").start())

        in_bus = stream_axis_bus(self.dut, "io_input_")
        self.axis_input = axi.AxiStreamSource(in_bus, self.dut.clk, self.dut.reset)
        self.axis_input.log.setLevel(logging.WARNING)

        out_buses = [
            stream_axis_bus(self.dut, f"io_outputs_{i}_") for i in range(self.lanes)
        ]
        self.axis_outputs = [
            axi.AxiStreamSink(bus, self.dut.clk, self.dut.reset) for bus in out_buses
        ]
        for axis in self.axis_outputs:
            axis.log.setLevel(logging.WARNING)

    async def reset(self):
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 2)

    async def run_test(self, n: int = 8):
        expected = np.random.bytes(n)
        sel = np.random.randint(self.lanes)

        self.axis_input.send_nowait(expected)

        self.dut.io_sel.value = sel
        self.dut.io_run.value = 1
        await ClockCycles(self.dut.clk, 1)
        self.dut.io_run.value = 0
        await ClockCycles(self.dut.clk, 5)

        await with_timeout(self.axis_input.idle_event.wait(), 1000, "ns")

        actual = self.axis_outputs[sel].read_nowait(n)
        actual = bytes(actual)

        assert actual == expected


@cocotb.test()
async def test_streamdemuxmetered(dut):
    tb = TB(dut)
    await tb.reset()

    for _ in range(100):
        await tb.run_test(8)

    # Try to send too much data
    try:
        await tb.run_test(16)
        assert False, "This should have thrown a timeout error"
    except cocotb.result.SimTimeoutError:
        pass
