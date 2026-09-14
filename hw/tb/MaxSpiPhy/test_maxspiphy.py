import cocotb
from cocotb.triggers import ClockCycles, RisingEdge, FallingEdge, with_timeout
from cocotbext import axi

import numpy as np
import sys
from pathlib import Path

from fpga_utils import TbTemplate, axis_sink, axis_source, corr, random_pause


class TB(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        self.input = axis_source(dut, "io_data_", byte_size=32)

    async def send_data(self, data: bytes):
        await self.input.write(data)
        await self.input.wait()


@cocotb.test()
async def test_dut(dut):
    tb = TB(dut)
    await tb.reset()

    await tb.send_data([0x8000000F])
    await tb.send_data([0x12345678])

    await ClockCycles(tb.dut.clk, 10000)


from fpga_utils import test_runner

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level='MaxSpiPhy',
        package='gps',
        proj_dir='../../..',
        source_dir='hw/spinal/gps',
        gen_dir='hw/gen',
    )
