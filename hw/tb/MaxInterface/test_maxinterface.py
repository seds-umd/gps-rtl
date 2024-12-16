#!/usr/bin/env python

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, with_timeout

import random
import numpy as np

import fpga_utils.spinal_stream as stream
from fpga_utils import TbTemplate, test_runner


def randbytes(n, b=8):
    for _ in range(n):
        yield random.getrandbits(b)


class Tb(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        # 4 cycles per 4.092 MHz clock cycle
        self._ser_clk = self.dut.io_max_clk_ser
        cocotb.start_soon(
            Clock(self._ser_clk, period=int(1e6 / (4.092 * 4)), units="ps").start()
        )

        self.out_bus = stream.SpinalStreamSink.from_prefix(dut, "io_iq")

    async def send_samples(self, samples: list):
        await RisingEdge(self.dut.io_max_clk_ser)

        for i in range(0, len(samples), 16):
            block = samples[i : i + 16]

            # I1, I0, Q1, Q0
            for idx in [(0, 1), (0, 0), (1, 1), (1, 0)]:
                for j in range(16):
                    self.dut.io_max_data_in.value = int(block[j, idx[0], idx[1]])

                    if j == 0 and idx == (0, 1):
                        self.dut.io_max_data_sync.value = 1
                    else:
                        self.dut.io_max_data_sync.value = 0

                    await RisingEdge(self.dut.io_max_clk_ser)

            # Add variable delay
            if (i // 16) % 4 == idx[0] + 2 * idx[1]:
                await ClockCycles(self.dut.io_max_clk_ser, (i // 16) % 16)

    def random_samples(self, count: int):
        # Generate random IQ samples
        bits_per_half_sample = 2
        # Samples formatted as [[[I0, I1], [Q0, Q1]]]*N
        samples = [
            [
                [random.getrandbits(1) for _ in range(bits_per_half_sample)]
                for _ in range(2)
            ]
            for _ in range(count)
        ]
        samples = np.array(samples)
        samples_ref = samples[:, :, 0] + 2 * samples[:, :, 1]

        return samples, samples_ref

    async def test(self, count: int):
        assert count % 16 == 0
        samples, ref = self.random_samples(count)

        await self.send_samples(samples)
        await ClockCycles(self._ser_clk, 64)

        samples_recv = (await with_timeout(self.out_bus.read(), 10000, "ns")).payload

        assert (samples_recv["c_re"] == ref[:, 0]).all()
        assert (samples_recv["c_im"] == ref[:, 1]).all()


@cocotb.test
async def test_interface(dut):
    tb = Tb(dut)
    await tb.reset()

    await tb.test(128)
    await tb.test(256)
    await tb.test(1024)


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="MaxInterface",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )
