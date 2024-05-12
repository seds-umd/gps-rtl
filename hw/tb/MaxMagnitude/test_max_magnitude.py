import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import numpy as np
import sys
from pathlib import Path

utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from fft_sim import pack_complex
from utils import TB_Template, axis_source, random_pause


class TB(TB_Template):
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
        data[i_max, j_max] *= np.random.uniform(0.3, 1) / np.abs(data[i_max, j_max])

        for i in range(size):
            self.dut.io_freq.value = int(freqs[i])

            await self.send_data(pack_complex(data[i]), exponent)

        # Finish transaction
        await self.input.wait()

        # Wait a few extra cycles
        await ClockCycles(self.dut.clk, 10)

        max_val = int(self.dut.io_max_mag)
        max_idx = int(self.dut.io_max_idx)
        max_freq = int(self.dut.io_max_freq.value.signed_integer) + int(size / 2)

        expected_max = np.max(np.abs(data)) * 128 * (1 << exponent)

        assert i_max == max_freq, f"Frequency expected: {i_max}, actual: {max_freq}"
        assert j_max == max_idx, f"Index expected: {j_max}, actual: {max_idx}"

        self.dut._log.info(f"Magnitude expected: {expected_max}, actual: {max_val}")


@cocotb.test()
async def test_dut(dut):
    tb = TB(dut)

    await tb.reset()

    for _ in range(16):
        await with_timeout(tb.test_grid(exponent=0), 100000, "ns")
