import cocotb
from cocotb.clock import Clock
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import logging
import numpy as np
import itertools

from fpga_utils import TbTemplate, axis_sink, axis_source


class TB(TbTemplate):
    def __init__(self, dut, lanes=4):
        self.lanes = lanes

        super().__init__(dut)

        self.axis_input = axis_source(dut, "io_input_")
        self.axis_outputs = [
            axis_sink(dut, f"io_outputs_{i}_") for i in range(self.lanes)
        ]

        self.axis_input.set_pause_generator(itertools.cycle([0, 1, 0, 0]))
        for sink in self.axis_outputs:
            sink.set_pause_generator(itertools.cycle([1, 1, 0, 0]))

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
        await ClockCycles(self.dut.clk, 10)

        actual = self.axis_outputs[sel].read_nowait(n)
        actual = bytes(actual)

        assert actual == expected
        assert all(sink.empty() for sink in self.axis_outputs)


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


from fpga_utils import test_runner

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level='StreamDemuxMeteredTest',
        scala_name='StreamDemuxMetered',
        scala_object='StreamDemuxMeteredVerilog',
        package='gps',
        proj_dir='../../..',
        source_dir='hw/spinal/gps',
        gen_dir='hw/gen',
    )
