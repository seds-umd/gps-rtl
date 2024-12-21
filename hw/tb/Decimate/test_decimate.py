#!/usr/bin/env python

import cocotb
from cocotb.triggers import ClockCycles

import numpy as np
import logging

from fpga_utils import TbTemplate, test_runner, random_pause
from fpga_utils import spinal_stream as stream
from fpga_utils.dsp import corr


class TB(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        self.in_bus = stream.SpinalStreamSource.from_prefix(self.dut, "io_iq_in")
        self.out_bus = stream.SpinalStreamSink.from_prefix(self.dut, "io_iq_out")

        # Random timing
        self.in_bus.set_pause_generator(random_pause())
        self.out_bus.set_pause_generator(random_pause())

    # Samples must be normalized to +-1
    async def run(self, samples: np.ndarray):
        samples_re = (samples.real * 127).astype(np.int8)
        samples_im = (samples.imag * 127).astype(np.int8)

        await self.in_bus.send({"re": samples_re, "im": samples_im})
        await self.in_bus.wait()
        await ClockCycles(self.dut.clk, 10)

        data = await self.out_bus.read(len(samples) // 8)
        data = data.payload

        data_re = np.array(data["re"], dtype=np.uint8).astype(np.int8)
        data_im = np.array(data["im"], dtype=np.uint8).astype(np.int8)
        data = data_re + 1j * data_im
        data /= 127

        return data

    async def reset(self):
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 0


@cocotb.test()
async def test_decimate(dut):
    tb = TB(dut)

    await tb.reset()

    for N in [16, 64, 256, 1024, 4096]:
        ref = np.random.randn(N) + 1j * np.random.randn(N)
        ref /= np.max(np.abs(ref))
        ref_dec = np.sum(ref.reshape(-1, 8), axis=1) / 8

        result = await tb.run(ref)
        dec_corr = corr(ref_dec, result)

        dut._log.info(f"N={N}, correlation={dec_corr:0.5f}")
        assert dec_corr > 0.99


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="Decimate",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )
