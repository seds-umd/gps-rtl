#!/usr/bin/env python

import cocotb
from cocotb.triggers import ClockCycles

import numpy as np
import matplotlib.pyplot as plt
import logging

import fpga_utils
import fpga_utils.spinal_stream as stream
from fpga_utils import TbTemplate, test_runner
from fpga_utils.cordic_sim import CordicSinCosSim, CordicAtan2Sim
from fpga_utils.dsp import corr, from_sfix
from gps import gps, gps_sim, prn_gen


def decode_complex_samples(payload: dict, prefix: str = None, width: int = 8):
    if prefix:
        re = np.array(payload[prefix + "_re"])
        im = np.array(payload[prefix + "_im"])
    elif "c_re" in payload.keys():
        re = np.array(payload["c_re"])
        im = np.array(payload["c_im"])
    else:
        re = np.array(payload["re"])
        im = np.array(payload["im"])

    if width <= 8:
        re = (re << (8 - width)).astype(np.int8)
        im = (im << (8 - width)).astype(np.int8)
    elif width <= 16:
        re = (re << (16 - width)).astype(np.int16)
        im = (im << (16 - width)).astype(np.int16)
    else:
        pass  # TODO

    samples = re + 1j * im

    return samples


def get_complex_samples(mon: stream.SpinalStreamMonitor, width: int = 8):
    data = mon.read_nowait()
    return decode_complex_samples(data.payload, width=width)


def decode_real_samples(payload: list, peak: int = 0, width: int = 8):
    data = [from_sfix(x, peak, width) for x in payload]
    return np.array(data)


def get_real_samples(mon: stream.SpinalStreamMonitor, peak: int = 0, width: int = 8):
    data = mon.read_nowait()
    return decode_real_samples(data.payload, peak, width)


class Tb(TbTemplate):
    def __init__(self, dut, debug=False):
        super().__init__(dut)

        self.fs = 4.092e6

        # Need to iterate through each level or it breaks the signal autodetection
        dir(self.dut.cordic_sincos)
        dir(self.dut.cordic_atan)

        self.cordic_sincos = CordicSinCosSim(self.dut.cordic_sincos.cordic)
        self.cordic_atan = CordicAtan2Sim(self.dut.cordic_atan.cordic)

        self.iq_bus = stream.SpinalStreamSource.from_prefix(self.dut, "io_iq")
        self.config = stream.SpinalStreamSource.from_prefix(self.dut, "io_config_flow")
        self.nav_data = stream.SpinalStreamSink.from_prefix(self.dut, "io_nav_data")
        self.debug_flow = stream.SpinalStreamSink.from_prefix(self.dut, "io_debug")

        if debug:
            self.frequency = stream.SpinalStreamMonitor.from_prefix(
                dut, "frequency_stream"
            )

    def set_config(self, sv: int, freq_offset: int, phase_offset: int):
        payload = {
            "sv": [sv - 1],
            "freq_offset": [freq_offset],
            "phase_offset": [phase_offset],
            "snr": [0],
        }

        self.config.send_nowait(payload)

    def send_generated_samples(
        self, count=1e5, sv=1, doppler=0, doppler2=0, sample_phase=0, noise=True
    ):
        # -128.5 is worst case real world received power
        power = -128.5 if noise else None

        # 3/4 is about optimal for 33% magnitude bit density (per MAX2769 datasheet)
        samples = (3 / 4 * 127) * gps_sim.generate_gps(
            f_s=self.fs,
            n=int(count),
            sv=sv,
            doppler=doppler,
            doppler2=doppler2,
            sample_phase=sample_phase,
            signal_power=power,
        )

        times_single = np.arange(4092)
        times = np.tile(times_single, int(len(samples) / 4092) + 1)
        times = times.astype(np.uint16)[0 : len(samples)]

        samples_re = samples.real.astype(np.int8).astype(np.uint8) >> 6
        samples_im = samples.imag.astype(np.int8).astype(np.uint8) >> 6

        payload = {"c_re": samples_re, "c_im": samples_im, "t": times}

        samples_re = ((samples_re << 6) | 0b100000).astype(np.int8)
        samples_im = ((samples_im << 6) | 0b100000).astype(np.int8)
        samples_biased = samples_re + 1j * samples_im

        self.iq_bus.send_nowait(payload)

        return samples, samples_biased

    def get_debug_data(self):
        frame = self.debug_flow.read_nowait()

        dec_early = decode_complex_samples(frame.payload, prefix="dec_early", width=14)
        dec_prompt = decode_complex_samples(
            frame.payload, prefix="dec_prompt", width=14
        )
        dec_late = decode_complex_samples(frame.payload, prefix="dec_late", width=14)

        carrier_err = decode_real_samples(frame.payload["carr_err"], peak=0, width=8)
        carrier_nco = (
            decode_real_samples(frame.payload["carr_nco"], peak=3, width=8) * 125 / 2**5
        )
        # code_err = decode_real_samples(frame.payload["code_err"])
        # code_nco = decode_real_samples(frame.payload["code_nco"])

        return dec_early, dec_prompt, dec_late, carrier_err, carrier_nco


@cocotb.test(skip=False)
async def test_tracking_debug(dut, graph=True):
    np.random.seed(958736385)
    tb = Tb(dut, debug=True)
    log = dut._log
    await tb.reset()

    sv = 1
    freq_offset = 1050
    code_phase = 10
    period = 4092

    N = period * 500  # ms of data

    tb.set_config(sv, int(freq_offset / 125), code_phase)
    samples, samples_biased = tb.send_generated_samples(
        N, doppler=freq_offset, doppler2=1, sample_phase=code_phase
    )

    await ClockCycles(dut.clk, int(N * 1.1))

    # Collect data
    frequencies = get_real_samples(tb.frequency, 8, 16) * 125

    dec_early, dec_prompt, dec_late, carrier_err, carrier_nco = tb.get_debug_data()

    # Reference GPS tracking
    (
        ref_prompt,
        ref_carr_freq,
        ref_carr_err,
        ref_code_freq,
        ref_code_err,
        ref_code_phase,
        _,
    ) = gps.tracking(samples_biased, tb.fs, sv, freq_offset, code_phase, True)

    dec_prompt /= np.max([np.abs(dec_prompt.real)])
    ref_prompt /= np.max(np.abs(ref_prompt))

    # Graphs
    if graph:
        rows = 3
        plt.figure(figsize=(8, 8), dpi=300)

        plt.subplot(rows, 2, 1)
        plt.title("Carrier Discriminator")
        plt.plot(carrier_err, label="sim")
        plt.plot(ref_carr_err, label="ref")
        plt.legend()

        plt.subplot(rows, 2, 2)
        plt.title("Carrier NCO")
        plt.plot(carrier_nco, label="sim")

        plt.subplot(rows, 2, 3)
        plt.title("Frequency Estimate")
        plt.plot(frequencies)
        plt.plot(ref_carr_freq)

        plt.subplot(rows, 2, 4)
        plt.title("Decimated Samples")
        plt.plot(dec_prompt.real, "-C0", label="sim re")
        plt.plot(dec_prompt.imag, "--C0", label="sim im")
        plt.plot(ref_prompt.real, "-C1", label="ref re")
        plt.plot(ref_prompt.imag, "--C1", label="ref im")

        plt.subplot(rows, 2, 5)
        plt.title("Code Discriminator")
        # plt.plot()
        plt.plot(ref_code_err)

        plt.subplot(rows, 2, 6)
        plt.title("Code Frequency")
        plt.plot(ref_code_freq)

        plt.tight_layout()
        plt.savefig("out1.png")


@cocotb.test(skip=True)
async def test_trackingchannel(dut):
    tb = Tb(dut)
    await tb.reset()

    sv = 1
    freq_offset = 1000
    code_phase = 10
    period = 4092

    # 100ms worth of samples
    N = period * 100

    tb.set_config(sv, int(freq_offset / 125), code_phase)
    samples = tb.send_generated_samples(
        N, doppler=freq_offset, doppler2=100, sample_phase=code_phase
    )

    await ClockCycles(dut.clk, int(N * 1.1))

    # Reference GPS tracking
    (
        ref_prompt,
        ref_carr_freq,
        ref_carr_err,
        ref_code_freq,
        ref_code_err,
        ref_code_phase,
        ref_code_pos,
    ) = gps.tracking(samples, tb.fs, sv, freq_offset, code_phase, True)


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="TrackingChannel",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
        verilog_sources=["hw/verilog/CordicSinCos.v", "hw/verilog/CordicAtan.v"],
    )
