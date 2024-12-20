#!/usr/bin/env python

import cocotb
from cocotb.triggers import ClockCycles

import fpga_utils
import fpga_utils.spinal_stream as stream
from fpga_utils import TbTemplate, test_runner
from fpga_utils.cordic_sim import CordicSim
from gps import gps_sim

import numpy as np


class Tb(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        self.fs = 4.092e6

        # Need to iterate through each level or it breaks the signal autodetection
        dir(self.dut.cordic)

        self.cordic_sim = CordicSim(self.dut.cordic.cordic)

        self.iq_bus = stream.SpinalStreamSource.from_prefix(self.dut, "io_iq")
        self.config = stream.SpinalStreamSource.from_prefix(self.dut, "io_config")
        self.nav_data = stream.SpinalStreamSink.from_prefix(self.dut, "io_nav_data")

    def set_config(self, sv: int, freq_offset: int, phase_offset: int):
        payload = {
            "sv": [sv],
            "freq_offset": [freq_offset],
            "phase_offset": [phase_offset],
            "snr": [0],
        }

        self.config.send_nowait(payload)

    def send_generated_samples(
        self, count=1e5, sv=1, doppler=0, sample_phase=0, noise=True
    ):
        # -128.5 is worst case real world received power
        power = -128.5 if noise else None

        # 3/4 is about optimal for 33% magnitude bit density (per MAX2769 datasheet)
        samples = (3 / 4 * 127) * gps_sim.generate_gps(
            f_s=self.fs,
            n=int(count),
            sv=sv,
            doppler=doppler,
            sample_phase=sample_phase,
            signal_power=power,
        )

        times_single = np.arange(4092)
        times = np.tile(times_single, int(len(samples) / 4092) + 1)
        times = times.astype(np.uint16)[0 : len(samples)]

        samples_re = samples.real.astype(np.int8).astype(np.uint8) >> 6
        samples_im = samples.imag.astype(np.int8).astype(np.uint8) >> 6

        payload = {
            "c_re": samples_re,
            "c_im": samples_im,
            "t": times
        }

        self.iq_bus.send_nowait(payload)

@cocotb.test
async def test_trackingchannel(dut):
    tb = Tb(dut)
    await tb.reset()

    # 100ms worth of samples
    N = 4092 * 1000

    sv = 1
    freq_offset = 0
    code_phase = 0

    tb.set_config(sv, int(freq_offset/125), code_phase)
    tb.send_generated_samples(N, doppler=freq_offset, sample_phase=code_phase)

    await ClockCycles(dut.clk, 100000)

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="TrackingChannel",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
        verilog_sources=["hw/verilog/CordicSinCos.v"],
    )
