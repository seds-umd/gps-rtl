import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import numpy as np
import sys
from pathlib import Path

utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from utils import TB_Template, axis_sink, axis_source


class TB(TB_Template):
    def __init__(self, dut, size):
        super().__init__(dut)

        self.size = size

        self.input = axis_source(dut, "io_input_", fragment=True)
        self.output = axis_sink(dut, "io_output_", fragment=True)
        self.set_pause(True)
        self.output.set_pause_generator(self.pause_gen())

        dut.io_output_offset.value = 0

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

    async def send_data(self, data: bytes):
        assert len(data) == self.size

        await self.input.send(data)
        await self.input.wait()

    async def get_data(self, offset=0):
        self.dut.io_output_offset.value = offset

        self.set_pause(False)
        frame: axi.AxiStreamFrame = await self.output.recv()
        self.set_pause(True)

        return frame.tdata


@cocotb.test()
async def test_stream_memory(dut):
    N = 16
    tb = TB(dut, N)

    await tb.reset()

    # Test with no offset
    for _ in range(100):
        expected = np.random.bytes(N)
        await tb.send_data(expected)
        actual = await tb.get_data()

        assert expected == actual

    # Test with offset
    for _ in range(100):
        offset = np.random.randint(N)

        expected = np.random.bytes(N)
        await tb.send_data(expected)
        actual = await tb.get_data(offset)

        # Apply offset to expected value
        expected = np.roll(list(expected), -offset).astype(np.uint8).tobytes()

        assert expected == actual
