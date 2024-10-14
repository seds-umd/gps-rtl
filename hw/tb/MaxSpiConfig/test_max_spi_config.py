import cocotb

from cocotb.clock import Clock 
from cocotb.triggers import ClockCycles

import sys
from pathlib import Path

utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from utils import TB_Template, axis_source

class TB(TB_Template):
    def __init__(self, dut):
        super().__init__(dut)

        self.input = axis_source(dut, "io_data_", byte_size=32)

    async def send_data(self, data: bytes):
        await self.input.write(data)
        await self.input.wait()

@cocotb.test()
async def test_three_wire_spi(dut):
    tb = TB(dut)
    await tb.reset()

    await tb.send_data([0x8000000F]*2)
    await tb.send_data([0x12345678])

    await ClockCycles(tb.dut.clk, 10000)
