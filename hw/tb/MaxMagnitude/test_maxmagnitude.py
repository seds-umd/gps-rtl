#!/usr/bin/env python

import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi
import numpy as np

from fpga_utils import TbTemplate, axis_source, test_runner
from fpga_utils.fft_sim import fft_pack_complex


class TB(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        self.dut.io_restart.value = 0

        self.input = axis_source(
            dut, "io_input_", fragment=True, user=True, byte_size=16
        )

    async def send_data(self, data: bytes, user: int):
        data = axi.AxiStreamFrame(data, tuser=user)
        await self.input.send(data)
        await self.input.wait()

    async def restart(self):
        self.dut.io_restart.value = 1
        await ClockCycles(self.dut.clk, 1)
        self.dut.io_restart.value = 0
        await ClockCycles(self.dut.clk, 1)

    async def test_grid(self, size: int = 16, exponent: int = 4):
        await self.restart()

        freqs = np.arange(size) - int(size / 2)

        i_max = np.random.randint(size)
        j_max = np.random.randint(size)

        data = np.random.uniform(-1, 1, (size, size))
        data = data + 1j * np.random.uniform(-1, 1, (size, size))
        data /= 4
        data[i_max, j_max] *= np.random.uniform(0.5, 1) / np.abs(data[i_max, j_max])

        for i in range(size):
            self.dut.io_freq.value = int(freqs[i])

            await self.send_data(fft_pack_complex(data[i]), exponent)

        # Finish transaction
        await self.input.wait()

        # Wait a few extra cycles
        await ClockCycles(self.dut.clk, 10)

        max_val = int(self.dut.io_max_mag)
        max_idx = int(self.dut.io_max_idx)
        max_freq = int(self.dut.io_max_freq.value.signed_integer)

        debug_info = f" ({i_max}, {j_max}) = {data[i_max, j_max]:.3f}, ({max_freq + int(size/2)}, {max_idx}) = {data[max_freq + int(size/2), max_idx]:.3f}"

        i_max -= int(size / 2)

        expected_max = np.max(np.abs(data)) * 128 * (1 << exponent)

        assert i_max == max_freq, (
            f"Frequency expected: {i_max}, actual: {max_freq}" + debug_info
        )
        assert j_max == max_idx, (
            f"Index expected: {j_max}, actual: {max_idx}" + debug_info
        )

        self.dut._log.info(
            f"Magnitude expected: {expected_max}, actual: {max_val}, diff: {(expected_max - max_val)/expected_max:0.3f}"
        )


@cocotb.test()
async def test_dut(dut):
    tb = TB(dut)

    await tb.reset()

    for i in range(16):
        await with_timeout(tb.test_grid(size=64, exponent=i), 100000, "ns")


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="MaxMagnitude",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )
