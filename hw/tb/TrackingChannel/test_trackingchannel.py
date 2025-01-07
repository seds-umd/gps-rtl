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


PLL_WIDTH = 16
PLL_ERR_PEAK = 0
PLL_CARR_NCO_PEAK = 3
PLL_CODE_NCO_PEAK = 7
PRN_FREQ_WIDTH = 28


# Modified PLL to match sim behavior
class PLL:
    def __init__(self, bw: float, zeta: float, gain: float, ts: float):
        """Phase locked loop

        Args:
            bw (float): Noise bandwidth
            zeta (float): Damping ratio
            gain (float): Loop gain
            ts (float): Sampling time
        """

        self.set_params(bw, zeta, gain, ts)
        self.reset()

    def set_params(self, bw: float, zeta: float, gain: float, ts: float):
        w_n = 8 * zeta * bw / (4 * zeta**2 + 1)
        tau1 = gain / (w_n * w_n)
        tau2 = 2 * zeta / w_n

        self.c1 = tau2 / tau1  # derivative term
        self.c2 = ts / tau1  # proportional term

    def update(self, err):
        # nco = self.last_nco + self.c1 * (err - self.last_err) + err * self.c2
        nco = self.c1 * (err - self.last_err) + err * self.c2

        self.last_err = err
        self.last_nco = nco

        return nco

    def reset(self):
        self.last_err = 0
        self.last_nco = 0


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


def quantize(val: int, peak: int, width: int):
    val = int(np.round(val * 2 ** (width - peak - 1))) / 2 ** (width - peak - 1)
    return val


def tracking_model(
    x: np.ndarray,
    f_s: float,
    sv: int,
    freq_est: float,
    code_est: int,
    debug_results: bool = False,
):
    freq_est = int(freq_est / 125)

    carrier_pll = PLL(10, 0.707, 0.25, 1e-3)
    code_dll = PLL(1, 0.707, 1, 1e-3)

    # Parameters
    ms_count = int(1e3 * len(x) / f_s)
    code_freq_basis = 1.023e6
    early_late_spacing = 0.5

    code_ref = prn_gen.generate(sv)
    code_ref = np.concatenate([[code_ref[-1]], code_ref, [code_ref[0]]])

    # Variables
    carrier_phase = 0
    carrier_freq = freq_est

    # code_phase = 0  # units of code chips
    code_phase = 0.5
    # code_phase = code_est
    code_freq = code_freq_basis

    sample_position = int(f_s / 1e3 - code_est)
    # sample_position = 0

    # Outputs
    res_samples = []

    # Debug outputs
    res_carr_freq = []
    res_carr_err = []
    res_carr_nco = []
    res_code_freq = []
    res_code_err = []
    res_code_nco = []
    res_code_phase = []
    res_code_pos = []

    for _ in range(ms_count):
        code_phase_step = code_freq / f_s
        blksize = int(np.ceil((1023 - code_phase) / code_phase_step))

        # Get chunk of data
        raw_signal = x[sample_position : sample_position + blksize]
        sample_position = sample_position + blksize

        # Exit if not enough samples
        if len(raw_signal) < blksize:
            break

        # Generate code replicas
        tcode = code_phase + np.arange(blksize, dtype=float) * code_phase_step
        prompt_code = code_ref[np.ceil(tcode).astype(int)]

        tcode_early = np.ceil(tcode - early_late_spacing).astype(int)
        early_code = code_ref[tcode_early]

        tcode_late = np.ceil(tcode + early_late_spacing).astype(int)
        late_code = code_ref[tcode_late]

        code_phase = tcode[-1] + code_phase_step - 1023

        # Advance phase
        phase_inc = carrier_freq / 2 ** (12 + 3 - 10)
        phase = phase_inc * np.arange(blksize + 1) + 2**10 * carrier_phase / (2 * np.pi)
        phase = phase * 2 * np.pi / 2**10
        carrier_phase = phase[-1] % (2 * np.pi)

        # Shift to DC, remove PRN, and sum
        baseband = raw_signal * np.exp(-1j * phase[:-1])

        # Match shift of 6 in Decimate
        prompt = np.sum(baseband * prompt_code) / 2**6
        early = np.sum(baseband * early_code) / 2**6
        late = np.sum(baseband * late_code) / 2**6

        # Update carrier PLL
        carrier_err = np.arctan(prompt.imag / prompt.real) / (2 * np.pi)
        carrier_err = quantize(carrier_err, PLL_ERR_PEAK, PLL_WIDTH)
        carrier_nco = carrier_pll.update(carrier_err) / 2**5
        carrier_nco = quantize(carrier_nco, PLL_CARR_NCO_PEAK, PLL_WIDTH)
        old_carr_freq = carrier_freq
        carrier_freq += carrier_nco

        # Update code DLL
        code_err = prompt.real * (early.real - late.real) + prompt.imag * (
            early.imag - late.imag
        )
        code_err /= blksize**2
        code_nco = code_dll.update(code_err)
        code_freq -= code_nco

        # Save stuff for graphing and debugging
        res_samples.append(prompt)

        if debug_results:
            res_carr_freq.append(old_carr_freq)
            res_carr_err.append(carrier_err)
            res_carr_nco.append(carrier_nco)

            res_code_freq.append(code_freq)
            res_code_err.append(code_err)
            res_code_nco.append(code_nco)
            res_code_phase.append(code_phase)
            res_code_pos.append(sample_position)

    res_samples = np.array(res_samples, dtype=np.complex64)

    if debug_results:
        return (
            np.array(res_samples),
            np.array(res_carr_freq),
            np.array(res_carr_err),
            np.array(res_carr_nco),
            np.array(res_code_freq),
            np.array(res_code_err),
            np.array(res_code_nco),
            np.array(res_code_phase),
            np.array(res_code_pos),
        )
    else:
        return res_samples


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

        self.dut.io_fb_enabled.value = 1

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

        carrier_err = decode_real_samples(frame.payload["carr_err"], peak=0, width=16)
        carrier_nco = decode_real_samples(frame.payload["carr_nco"], peak=4, width=16)
        carrier_nco *= 125  # Scale to Hz
        carrier_nco /= 2**5  # Match shift of 5 to carrier_freq_est

        code_err = decode_real_samples(frame.payload["code_err"], peak=0, width=16)
        code_nco = np.array(frame.payload["code_nco"]).astype(np.int16).astype(np.float64)
        code_nco *= 1.023e6 / 2**PRN_FREQ_WIDTH

        return (
            dec_early,
            dec_prompt,
            dec_late,
            carrier_err,
            carrier_nco,
            code_err,
            code_nco,
        )


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

    N = period * 100  # ms of data

    tb.set_config(sv, int(freq_offset / 125), code_phase)
    np.random.seed(259879342)
    samples, samples_biased = tb.send_generated_samples(
        N, doppler=freq_offset, doppler2=-2, sample_phase=code_phase - 0.5
    )

    await ClockCycles(dut.clk, int(N * 1.1))

    # Collect data
    frequencies = get_real_samples(tb.frequency, 8, 16) * 125

    dec_early, dec_prompt, dec_late, carrier_err, carrier_nco, code_err, code_nco = (
        tb.get_debug_data()
    )
    dropped_samples = int(tb.dut.prn_1.dropped_iq_value.value)

    # Reference GPS tracking
    (
        ref_prompt,
        ref_carr_freq,
        ref_carr_err,
        ref_carr_nco,
        ref_code_freq,
        ref_code_err,
        ref_code_nco,
        ref_code_phase,
        _,
    ) = tracking_model(
        samples_biased, tb.fs, sv, freq_offset, (code_phase) % 4092, True
    )
    ref_carr_freq *= 125
    ref_carr_nco *= 125

    code_err_calc = dec_prompt.real * (dec_early.real - dec_late.real) + dec_prompt.imag * (
        dec_early.imag - dec_late.imag
    )
    code_err_calc /= 2**26

    # Graphs
    if graph:
        rows = 4
        plt.figure(figsize=(8, 12), dpi=300)

        plt.subplot(rows, 2, 1)
        plt.title("Carrier Discriminator")
        plt.plot(carrier_err, label="sim")
        plt.plot(ref_carr_err, label="ref")
        plt.legend()

        plt.subplot(rows, 2, 2)
        plt.title("Carrier NCO")
        plt.plot(carrier_nco, label="sim")
        plt.plot(ref_carr_nco, label="ref")

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
        plt.plot(code_err)
        plt.plot(ref_code_err)
        plt.plot(code_err_calc, "--C0")

        plt.subplot(rows, 2, 6)
        plt.title("Code NCO")
        plt.plot(code_nco)
        plt.plot(ref_code_nco)

        plt.subplot(rows, 2, (7, 8))
        plt.title("Code Frequency")
        plt.plot(1.023e6 + np.cumsum(code_nco))
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
