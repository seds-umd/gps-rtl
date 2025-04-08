#! /usr/bin/env python

import cocotb
from cocotb.triggers import ClockCycles

import numpy as np

import fpga_utils.spinal_stream as stream
from fpga_utils import TbTemplate, test_runner, to_twos_comp, from_twos_comp

IN_WIDTH = 16
OUT_WIDTH = 8

def bounds(val: int, width: int):
    if val >= 2**(width-1):
        return False
    elif val < -2**(width-1):
        return False
    else:
        return True

def model(re: int, im: int):
    re = (re << 8) | (0xFF if re & 0b1 else 0)
    im = (im << 8) | (0xFF if im & 0b1 else 0)

    while not (bounds(re, OUT_WIDTH) and bounds(im, OUT_WIDTH)):
        re >>= 1
        im >>= 1

    return re, im

class Tb(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        self.input = stream.SpinalStreamSource.from_prefix(dut, "io_input")
        self.output = stream.SpinalStreamSink.from_prefix(dut, "io_output")

    def send(self, re: int, im: int):
        payload = {
            "re": [to_twos_comp(re, width=IN_WIDTH)],
            "im": [to_twos_comp(im, width=IN_WIDTH)],
        }

        self.input.send_nowait(payload)

    async def get(self):
        payload = (await self.output.read(1)).payload

        re = payload["re"][0]
        im = payload["im"][0]

        re = from_twos_comp(re, width=OUT_WIDTH)
        im = from_twos_comp(im, width=OUT_WIDTH)

        return re, im
    
    async def test(self, re: int, im: int):
        assert bounds(re, IN_WIDTH)
        assert bounds(im, IN_WIDTH)

        self.send(re, im)
        re2, im2 = await self.get()

        re_ref, im_ref = model(re, im)

        assert re2 == re_ref and im2 == im_ref, f"{re, im} -> {re2, im2} / {re_ref, im_ref}"

@cocotb.test(timeout_time=1000, timeout_unit="us")
async def test_shiftgain(dut):
    np.random.seed(482829343)

    tb = Tb(dut)
    await tb.reset()

    numbers = [1, -1, 5, -5, 100, -100, 2**(IN_WIDTH-1)-1, -2**(IN_WIDTH-1)]

    for re in numbers:
        for im in numbers:
            await tb.test(re, im)

    for _ in range(10000):
        re = np.random.randint(-2**(IN_WIDTH-1), 2**(IN_WIDTH-1))
        im = np.random.randint(-2**(IN_WIDTH-1), 2**(IN_WIDTH-1))

        await tb.test(re, im)


def main():
    test_runner.run_wrapper(
        top_level="ShiftGain",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )

if __name__ == "__main__":
    main()
