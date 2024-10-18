#!/usr/bin/env python

import cocotb
from cocotb.triggers import ClockCycles

from fpga_utils import spinal_stream as stream
from fpga_utils import test_runner
from fpga_utils.testbench import TbTemplate
from fpga_utils.cordic_sim import CordicSim, encode_phase, decode_complex


class Tb(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut, "aclk")

        self.sim = CordicSim(dut)

        self.phase = stream.SpinalStreamSource.from_prefix(
            self.dut, "s_axis_phase", "aclk", "aresetn", axis=True
        )
        self.dout = stream.SpinalStreamSink.from_prefix(
            self.dut, "m_axis_dout", "aclk", "aresetn", axis=True
        )

    def write_phase(self, phase: int, user: int):
        # phase is 0-1023

        assert phase >= 0
        assert phase < 1024

        if phase > 2**9:
            phase

        user &= 0b111
        frame = {"tdata": [phase], "tuser": [user]}
        self.phase.write_nowait(frame)


@cocotb.test
async def test_cordic(dut):
    tb = Tb(dut)

    phases = [0, 5, 256, 500, 700, 1000, 1023]

    for phase in phases:
        tb.write_phase(phase, 0)

    await ClockCycles(dut.aclk, 100)


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="XilinxCORDIC",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
        verilog_sources=["hw/verilog/XilinxCORDIC.v"],
        scala=False,
    )
