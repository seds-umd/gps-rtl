import cocotb
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge, with_timeout

import sys
from pathlib import Path

from fpga_utils import TbTemplate

import random


class TB(TbTemplate):
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


from fpga_utils import test_runner

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level='Snr',
        package='gps',
        proj_dir='../../..',
        source_dir='hw/spinal/gps',
        gen_dir='hw/gen',
    )
