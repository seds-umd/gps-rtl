import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import numpy as np
import sys
from pathlib import Path

utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from fft_sim import pack_complex, unpack_complex
from utils import TB_Template, axis_sink, axis_source, corr, random_pause


class TB(TB_Template):
    def __init__(self, dut):
        super().__init__(dut)

        self.input = axis_source(dut, "io_input_", fragment=True, byte_size=16)
        self.output = axis_sink(dut, "io_mag_", fragment=True)
        self.output.set_pause_generator(random_pause())

    async def send_data(self, data: bytes):
        await with_timeout(self.input.send(data), 1000000, "ns")
        await with_timeout(self.input.wait(), 1000000, "ns")

    async def get_data(self):
        frame: axi.AxiStreamFrame = await with_timeout(
            self.output.recv(), 1000000, "ns"
        )

        return frame.tdata


@cocotb.test()
async def test_magnitude_stream(dut):
    tb = TB(dut)

    await tb.reset()

    N = 1024
    runs = 8

    for _ in range(runs):
        data = np.random.uniform(-1, 1, N) + 1j * np.random.uniform(-1, 1, N)

        await tb.send_data(pack_complex(data))

        expected = np.abs(data)
        actual = await tb.get_data()
        mag_corr = corr(expected, actual)

        tb.dut._log.info(f"Correlation: {mag_corr:0.3f}")
