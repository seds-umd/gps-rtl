#!/usr/bin/env python

import cocotb
from cocotb.triggers import ClockCycles

import numpy as np
from gps import prn_gen

import fpga_utils.spinal_stream as stream
from fpga_utils import TbTemplate, corr, random_pause, test_runner


COUNTER_WIDTH = 28


class TB(TbTemplate):
    def __init__(self, dut, period=10):
        super().__init__(dut, period=period)

        self.sv = stream.SpinalStreamSource.from_prefix(dut, "io_sv")
        self.freq_adj = stream.SpinalStreamSource.from_prefix(dut, "io_freq_adj")
        self.output = stream.SpinalStreamSink.from_prefix(dut, "io_code")

    async def set_params(self, sv=1, divider=1.0):
        self.dut.io_ratio.value = int(2 ** (COUNTER_WIDTH) / divider)
        self.sv.send_nowait([sv - 1])

    # adj is relative
    async def run_test(self, sv=1, divider=1.0, adj=0, length=1):
        await self.reset()
        await self.set_params(sv, divider)

        if adj != 0:
            adj_int = 2**COUNTER_WIDTH * adj
            divider = divider / (1 + adj)
            await self.freq_adj.send([adj_int])

        await ClockCycles(self.dut.clk, 1)

        # Clear internal buffer
        self.output.read_nowait()

        code_len = int(np.ceil(1023 * divider * length))
        expected = np.array(
            prn_gen.sample(sv, 1.023e6 * divider, code_len).real, dtype=int
        )

        while self.output.queue_len_bytes < code_len:
            await ClockCycles(self.dut.clk, 10)

        actual = np.array(self.output.read_nowait(code_len).payload)
        actual[actual == 0] = -1

        code_corr = corr(expected, actual)
        self.dut._log.info(f"SV={sv}, div={divider:0.4f}, corr={code_corr}")

        if code_corr < 0.99:
            print("actual  ", actual[:20], actual[-20:])
            print("expected", expected[:20], expected[-20:])

        assert code_corr > 0.99


@cocotb.test()
async def all_prns(dut):
    tb = TB(dut)
    np.random.seed(7598238)

    for sv in range(1, 33):
        await tb.run_test(sv)


@cocotb.test()
async def dividers(dut):
    tb = TB(dut)
    np.random.seed(509238798)

    for divider in [1.0, 5 / 3, 2.9999, 4]:
        for _ in range(5):
            sv = np.random.randint(1, 33)

            await tb.run_test(sv, divider)


@cocotb.test()
async def pauses(dut):
    tb = TB(dut)
    np.random.seed(239842039)

    tb.output.set_pause_generator(random_pause())

    for _ in range(5):
        sv = np.random.randint(1, 33)

        await tb.run_test(sv)


@cocotb.test()
async def frequency_adjust(dut):
    tb = TB(dut)
    np.random.seed(58390239)

    for adj in [1e-6, -1e-6, 10e-6, -10e-6]:
        sv = np.random.randint(1, 33)

        # Fails when length=10 but DLL noise will be more significant anyway
        await tb.run_test(sv, 4, adj, length=5)


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="Prn",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )
