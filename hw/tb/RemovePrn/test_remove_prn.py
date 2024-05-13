import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import numpy as np
import sys
from pathlib import Path
from gps import prn

utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from fft_sim import unpack_complex
from utils import TB_Template, axis_sink, axis_source, corr, generate_gps_samples


class TB(TB_Template):
    def __init__(self, dut):
        super().__init__(dut)

        self.input = axis_source(dut, "io_input_", byte_size=16)
        self.output = axis_sink(dut, "io_output_", byte_size=16)
        self.input.set_pause_generator(self.iq_pause())

        self.dut.io_sv.value = 0
        self.dut.io_set.value = 0
        self.dut.io_phase_offset.value = 0

    # Simulate sample rate
    def iq_pause(self, f=50, fs=4.092):
        x = 0

        while True:
            x += 1 / f

            if x > 1 / fs:
                x -= 1 / fs
                yield False
            else:
                yield True

    async def send_data(self, data):
        await self.input.send(data)
        await self.input.wait()

    async def get_data(self):
        frame: axi.AxiStreamFrame = await self.output.read()

        return frame

    async def configure(self, sv: int = 1, offset: int = 0):
        self.dut.io_sv.value = sv - 1
        self.dut.io_phase_offset.value = offset
        self.dut.io_set.value = 1
        await ClockCycles(self.dut.clk, 1)
        self.dut.io_set.value = 0
        await ClockCycles(self.dut.clk, 1)


@cocotb.test()
async def test_dut(dut):
    tb = TB(dut)

    await tb.reset()

    offset = 1234
    await tb.configure(offset=1234)
    bits, samples, quant = generate_gps_samples(4.092e6, 4096, 1, 0, offset, -120)

    await with_timeout(tb.send_data(bits), 1000000, "ns")

    # Receive data
    actual = await tb.get_data()
    actual = unpack_complex(actual)

    # Reference data
    prn_data = prn.sample(1, 4.092e6, 4096, offset_samples=offset)
    mixed = quant * prn_data
    mixed = mixed[len(mixed) - len(actual):]

    print(len(mixed), len(actual))
    print(corr(mixed, actual))
