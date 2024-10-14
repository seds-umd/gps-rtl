import cocotb
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import numpy as np
import sys
from pathlib import Path

utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from utils import TB_Template, axis_sink, axis_source, corr, random_pause


class TB(TB_Template):
    def __init__(self, dut):
        super().__init__(dut)

        self.input = axis_source(dut, "io_input_", fragment=True)
        self.output = axis_sink(dut, "io_output_", fragment=True)
        self.output.set_pause_generator(random_pause())

    async def send_data(self, data: bytes):
        await self.input.send(data)
        await self.input.wait()

    async def get_data(self):
        frame: axi.AxiStreamFrame = await self.output.recv()

        return frame.tdata


@cocotb.test()
async def test_dut(dut):
    tb = TB(dut)

    await tb.reset()
