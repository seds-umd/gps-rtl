#!/usr/bin/env python

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles

import numpy as np
from gps import prn_gen

from fpga_utils import TbTemplate, axis_sink, corr, random_pause, test_runner


class TB(TbTemplate):
    def __init__(self, dut, period=10):
        super().__init__(dut, period=period)

        self.output = axis_sink(dut, "io_code_", byte_size=1)

        dut.io_sv.value = 0
        dut.io_set.value = 0

    async def set_params(self, sv=1, divider=1.0):
        self.dut.io_sv.value = sv - 1
        self.dut.io_inc.value = int(2**16 / divider)
        self.dut.io_set.value = 1
        await RisingEdge(self.dut.clk)
        self.dut.io_set.value = 0

    async def run_test(self, sv=1, divider=1.0):
        await self.set_params(sv, divider)

        # Clear internal buffer
        self.output.read_nowait()

        code_len = int(np.ceil(1023 * divider))
        expected = np.array(
            prn_gen.sample(sv, 1.023e6 * divider, code_len).real, dtype=int
        )

        while self.output.queue_occupancy_bytes < code_len:
            await ClockCycles(self.dut.clk, 10)

        actual = np.array(await self.output.read(code_len))
        actual[actual == 0] = -1

        code_corr = corr(expected, actual)
        self.dut._log.info(f"SV={sv}, div={divider:0.3f}, corr={code_corr}")
        assert code_corr > 0.99


@cocotb.test()
async def test_prn(dut):
    tb = TB(dut)

    await tb.reset()

    # Test all SVs
    for sv in range(1, 33):
        await tb.run_test(sv)

    # Test different dividers
    for divider in [1.0, 5 / 3, 2.9999, 4]:
        for _ in range(5):
            sv = np.random.randint(1, 33)

            await tb.run_test(sv, divider)

    # Test pauses
    tb.output.set_pause_generator(random_pause())

    for _ in range(5):
        sv = np.random.randint(1, 33)

        await tb.run_test(sv)


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="Prn",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )
