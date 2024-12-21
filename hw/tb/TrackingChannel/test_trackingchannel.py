#!/usr/bin/env python

import cocotb
from cocotb.triggers import ClockCycles

import numpy as np
import matplotlib.pyplot as plt

import fpga_utils
import fpga_utils.spinal_stream as stream
from fpga_utils import TbTemplate, test_runner
from fpga_utils.cordic_sim import CordicSim
from fpga_utils.dsp import corr, from_sfix
from gps import gps, gps_sim, prn_gen


def get_complex_samples(mon: stream.SpinalStreamMonitor, width: int = 8):
    data = mon.read_nowait()

    if "c_re" in data.payload.keys():
        re = np.array(data.payload["c_re"])
        im = np.array(data.payload["c_im"])
    else:
        re = np.array(data.payload["re"])
        im = np.array(data.payload["im"])

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


def get_real_samples(mon: stream.SpinalStreamMonitor, peak: int = 0, width: int = 8):
    data = mon.read_nowait()

    samples = [from_sfix(x, peak, width) for x in data.payload]
    samples = np.array(samples)

    return samples


class Tb(TbTemplate):
    def __init__(self, dut, debug=False):
        super().__init__(dut)

        self.fs = 4.092e6

        # Need to iterate through each level or it breaks the signal autodetection
        dir(self.dut.cordic)

        self.cordic_sim = CordicSim(self.dut.cordic.cordic)

        self.iq_bus = stream.SpinalStreamSource.from_prefix(self.dut, "io_iq")
        self.config = stream.SpinalStreamSource.from_prefix(self.dut, "io_config")
        self.nav_data = stream.SpinalStreamSink.from_prefix(self.dut, "io_nav_data")

        if debug:
            self.iq_mon = stream.SpinalStreamMonitor.from_prefix(self.dut, "iq_biased")
            self.carrier_removed = stream.SpinalStreamMonitor.from_prefix(
                self.dut.prn_1, "io_input"
            )
            self.prn_removed = stream.SpinalStreamMonitor.from_prefix(
                self.dut.prn_1, "io_prompt"
            )
            self.prompt_decimated = stream.SpinalStreamMonitor.from_prefix(
                self.dut.dec_prompt, "io_iq_out"
            )
            self.carrier_pll_err = stream.SpinalStreamMonitor.from_prefix(
                self.dut.carrier_pll, "io_err"
            )
            self.carrier_pll_nco = stream.SpinalStreamMonitor.from_prefix(
                self.dut.carrier_pll, "io_nco"
            )
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

        payload = {"c_re": samples_re, "c_im": samples_im, "t": times}

        self.iq_bus.send_nowait(payload)

        return samples


@cocotb.test
async def test_tracking_debug(dut, graph=True):
    # np.random.seed(958736385)
    tb = Tb(dut, debug=True)
    log = dut._log
    await tb.reset()

    sv = 1
    freq_offset = 1000
    code_phase = 10
    period = 4092

    N = period * 10  # ms of data

    tb.set_config(sv, int(freq_offset / 125), code_phase)
    samples = tb.send_generated_samples(N*5, doppler=freq_offset, sample_phase=code_phase)

    await ClockCycles(dut.clk, int(N * 1.1))

    # Collect data
    cordic_phases = np.array(tb.cordic_sim.past_inputs)
    cordic_outputs = np.array(tb.cordic_sim.past_outputs)
    samples_biased = get_complex_samples(tb.iq_mon, width=8)
    carrier_removed = get_complex_samples(tb.carrier_removed, width=8)
    prn_removed = get_complex_samples(tb.prn_removed, width=8)
    prn_removal_dropped = int(dut.prn_1.io_dropped.value)
    prompt_decimated = get_complex_samples(tb.prompt_decimated, width=14)
    carrier_err = get_real_samples(tb.carrier_pll_err, width=8)
    frequencies = get_real_samples(tb.frequency, 8, 16) * 125

    # Reference data
    carrier_removed_ref = samples_biased * np.exp(
        1j * cordic_phases[: len(samples_biased)]
    )
    prn_removed_ref = carrier_removed * prn_gen.sample(
        sv, tb.fs, len(carrier_removed), offset_samples=code_phase + 1
    )  # TODO: why +1?
    prn_removed_ref = prn_removed_ref[prn_removal_dropped:]

    dec_count = len(prn_removed) // period
    prompt_decimated_ref = (
        prn_removed[: dec_count * period].reshape(-1, period).sum(axis=1)
    )

    # Reference GPS tracking
    (
        _,
        ref_carr_freq,
        ref_carr_err,
        ref_code_freq,
        ref_code_err,
        ref_code_phase,
        ref_code_pos,
    ) = gps.tracking(samples, tb.fs, sv, freq_offset, code_phase, True)
    # ) = gps.tracking(samples_biased, tb.fs, sv, freq_offset, code_phase, True)

    # Graphs
    if graph:
        graphs = 5
        plt.figure(figsize=(6, 12), dpi=300)

        plt.subplot(graphs, 1, 1)
        plt.title("CORDIC Phase")
        plt.plot(cordic_phases)

        plt.subplot(graphs, 1, 2)
        plt.title("Phase Derivative")
        freq = np.diff(np.unwrap(cordic_phases))
        freq = freq[: 1023 * (len(freq) // 1023)]
        freq = np.mean(freq.reshape(-1, 1023), axis=1) * tb.fs / (2 * np.pi)
        plt.plot(freq)

        plt.subplot(graphs, 1, 3)
        plt.title("CORDIC Output")
        plt.plot(cordic_outputs.real)
        plt.plot(cordic_outputs.imag)

        plt.subplot(graphs, 1, 4)
        plt.title("Carrier Discriminator")
        plt.plot(carrier_err, label="sim")
        plt.plot(ref_carr_err, label="ref")
        plt.legend()

        plt.subplot(graphs, 1, 5)
        plt.title("Frequency Estimate")
        plt.plot(frequencies)
        plt.plot(ref_carr_freq)

        plt.tight_layout()
        plt.savefig("out1.png")

        plt.figure(figsize=(6, 6), dpi=300)
        plt.scatter(
            prompt_decimated.real,
            prompt_decimated.imag,
            c=np.arange(len(prompt_decimated.real)),
        )
        plt.colorbar()
        plt.tight_layout()
        plt.savefig("out2.png")

    # Check carrier removal
    corr_carrier_removed = corr(carrier_removed_ref, carrier_removed)
    log.info(f"Carrier removal correlation: {corr_carrier_removed:0.3f}")
    assert corr_carrier_removed > 0.99

    # Check PRN removal
    corr_prn_removed = corr(prn_removed_ref, prn_removed)
    log.info(f"PRN removal correlation: {corr_prn_removed:0.3f}")
    assert corr_prn_removed > 0.99

    # Check decimated samples
    corr_prompt_decimated = corr(prompt_decimated, prompt_decimated_ref)
    log.info(f"Prompt decimated correlation: {corr_prompt_decimated:0.3f}")
    assert corr_prompt_decimated > 0.99


# @cocotb.test
async def test_trackingchannel(dut):
    tb = Tb(dut)
    await tb.reset()

    # 100ms worth of samples
    N = 4092 * 1000

    sv = 1
    freq_offset = 0
    code_phase = 0

    tb.set_config(sv, int(freq_offset / 125), code_phase)
    tb.send_generated_samples(N, doppler=freq_offset, sample_phase=code_phase)

    await ClockCycles(dut.clk, 10000)


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="TrackingChannel",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
        verilog_sources=["hw/verilog/XilinxCORDIC.v"],
    )
