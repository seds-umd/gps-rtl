import cocotb
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge, with_timeout

import sys
from pathlib import Path

utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from utils import TB_Template

import random


class TB(TB_Template):
    def __init__(self, dut):
        super().__init__(dut)

    async def run_test(self, num: int, den: int):
        self.dut.io_num.value = num
        self.dut.io_den.value = den

        self.dut.io_start.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.io_start.value = 0

        await with_timeout(FallingEdge(self.dut.io_busy), 1000, "ns")
        await RisingEdge(self.dut.clk)

        res = self.dut.io_res.value
        rem = self.dut.io_rem.value

        assert res == num // den
        assert rem == num % den


@cocotb.test()
async def test_snr(dut):
    tb = TB(dut)
    await tb.reset()

    for _ in range(100):
        num = random.randint(1, 2**32 - 1)
        den = random.randint(1, 2**32 - 1)

        await tb.run_test(num, den)
