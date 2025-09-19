import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import numpy as np

from fpga_utils import TbTemplate, axis_sink, axis_source


class TB(TbTemplate):
    def __init__(self, dut, size):
        super().__init__(dut)

        self.size = size

        self.input = axis_source(dut, "io_input_", fragment=True)
        self.output = axis_sink(dut, "io_output_", fragment=True)
        self.set_pause(True)
        self.output.set_pause_generator(self.pause_gen())

        self.random_pause = False

        dut.io_output_offset.value = 0

    def set_pause(self, val=True):
        self.paused = val
        self.output.pause = val

        # Can't rely on axis internal pause handling to set tready in this cycle
        if val:
            self.output.bus.tready.value = 0

    def pause_gen(self):
        while True:
            if self.paused or (
                self.dut.io_output_payload_last.value == 1
                and self.output.bus.tready.value == 1
            ):
                self.paused = True
                yield True

            elif self.random_pause:
                yield np.random.rand() < 0.5

            else:
                yield False

    async def send_data(self, data: bytes):
        assert len(data) == self.size

        await self.input.send(data)
        await self.input.wait()

    async def get_data(self, offset=0):
        self.dut.io_output_offset.value = offset

        self.set_pause(False)
        frame: axi.AxiStreamFrame = await with_timeout(
            self.output.recv(), self.period * 1e5, "ns"
        )

        self.set_pause(True)

        return frame.tdata

    async def run_test(self, count, offset):
        self.dut._log.info(f"Running with N={count}, offset={offset}")
        for _ in range(count):
            data = np.random.bytes(self.size)
            await self.send_data(data)
            actual = await self.get_data(offset)
            expected = np.roll(list(data), -offset).astype(np.uint8).tobytes()
            assert expected == actual


@cocotb.test(2, "ms")
async def test_stream_memory(dut):
    N = 16
    RUNS = 1000
    tb = TB(dut, N)

    await tb.reset()

    # Test w/o random pauses
    tb.random_pause = False
    await tb.run_test(RUNS, 0)  # No offset
    await tb.run_test(RUNS, np.random.randint(N))  # Random offset

    # Test with random pauses
    tb.random_pause = True
    await tb.run_test(RUNS, 0)  # No offset
    await tb.run_test(RUNS, np.random.randint(N))  # Random offset