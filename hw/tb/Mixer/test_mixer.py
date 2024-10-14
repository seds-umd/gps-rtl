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

        self.input_a = axis_source(dut, "io_input_a_", fragment=True, byte_size=16)
        self.input_b = axis_source(dut, "io_input_b_", fragment=True, byte_size=16)
        self.output = axis_sink(dut, "io_output_", fragment=True, byte_size=16)

        self.output.set_pause_generator(random_pause())

    def set_pause(self, val=True):
        self.paused = val
        self.output.pause = val

        # Can't rely on axis internal pause handling to set tready in this cycle
        if val:
            self.output.bus.tready.value = 0

    def pause_gen(self):
        while True:
            if self.paused or self.dut.io_output_payload_last.value == 1:
                self.paused = True

                yield True
            else:
                yield False

    async def send_data(self, data_a: bytes, data_b: bytes):
        assert len(data_a) == len(data_b)

        self.input_a.send_nowait(data_a)
        self.input_b.send_nowait(data_b)

        await with_timeout(self.input_a.wait(), len(data_a) * self.period * 10, "ns")

    async def get_data(self):
        frame: axi.AxiStreamFrame = await with_timeout(
            self.output.recv(), self.period * 1e5, "ns"
        )

        return frame.tdata


@cocotb.test()
async def test_dut(dut):
    tb = TB(dut)
    await tb.reset()

    N = 1024

    for _ in range(16):
        a = np.random.uniform(-1, 1, N) + 1j * np.random.uniform(-1, 1, N)
        b = np.random.uniform(-1, 1, N) + 1j * np.random.uniform(-1, 1, N)

        await tb.send_data(pack_complex(a), pack_complex(b))

        expected = a * b
        actual = unpack_complex(await tb.get_data())
        mix_corr = corr(expected, actual)

        tb.dut._log.info(f"Correlation: {mix_corr:0.3f}")
        assert mix_corr > 0.99
