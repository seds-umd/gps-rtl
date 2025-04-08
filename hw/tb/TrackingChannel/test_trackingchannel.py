#!/usr/bin/env python

import cocotb
from cocotb.triggers import ClockCycles

import numpy as np
import pickle
import datetime

import common
import graph
import fpga_utils.spinal_stream as stream
from fpga_utils import TbTemplate, test_runner
from fpga_utils.cordic_sim import CordicSinCosSim, CordicAtan2Sim
from fpga_utils.dsp import corr, from_sfix, from_twos_comp
from gps import gps_sim


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
    def __init__(self, dut):
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

        dec_early = decode_complex_samples(
            frame.payload, prefix="dec_early", width=common.DEC_WIDTH
        )
        dec_prompt = decode_complex_samples(
            frame.payload, prefix="dec_prompt", width=common.DEC_WIDTH
        )
        dec_late = decode_complex_samples(
            frame.payload, prefix="dec_late", width=common.DEC_WIDTH
        )

        carrier_err = decode_real_samples(
            frame.payload["carr_err"], peak=common.PLL_ERR_PEAK, width=common.PLL_WIDTH
        )
        carrier_nco = decode_real_samples(
            frame.payload["carr_nco"],
            peak=common.PLL_CARR_NCO_PEAK,
            width=common.PLL_WIDTH,
        )

        code_err = decode_real_samples(
            frame.payload["code_err"], peak=common.PLL_ERR_PEAK, width=common.PLL_WIDTH
        )
        code_nco = decode_real_samples(
            frame.payload["code_nco"],
            peak=common.PLL_CODE_NCO_PEAK,
            width=common.PLL_WIDTH,
        )

        carr_freq = decode_real_samples(
            frame.payload["carr_freq"],
            peak=common.CARR_FREQ_PEAK,
            width=common.CARR_FREQ_WIDTH,
        )

        code_freq_offset = frame.payload["code_freq_offset"]
        code_freq_offset = [
            from_twos_comp(x, width=common.PRN_FREQ_WIDTH - 12)
            for x in code_freq_offset
        ]
        code_freq_offset = np.array(code_freq_offset)

        return (
            dec_early,
            dec_prompt,
            dec_late,
            carrier_err,
            carrier_nco,
            code_err,
            code_nco,
            carr_freq,
            code_freq_offset,
        )


@cocotb.test(skip=False)
async def test_tracking_graph(dut):
    np.random.seed(958736385)
    tb = Tb(dut)
    log = dut._log
    log.info(f"Starting at {datetime.datetime.now().isoformat()}")
    await tb.reset()

    sv = 1
    freq_offset = 1050
    code_phase = 10
    period = 4092

    N = period * 10  # ms of data

    tb.set_config(sv, int(freq_offset / 125), code_phase)
    np.random.seed(259879342)
    samples, samples_biased = tb.send_generated_samples(
        N, doppler=freq_offset, doppler2=-2, sample_phase=code_phase - 0.5
    )

    await ClockCycles(dut.clk, int(N * 1.1))

    (
        dec_early,
        dec_prompt,
        dec_late,
        carrier_err,
        carrier_nco,
        code_err,
        code_nco,
        carr_freq,
        code_freq_offset,
    ) = tb.get_debug_data()

    save_data = {
        "sv": sv,
        "freq_offset": freq_offset,
        "code_phase": code_phase,
        "sample_count": N,
        "dec_early": dec_early,
        "dec_prompt": dec_prompt,
        "dec_late": dec_late,
        "carrier_err": carrier_err,
        "carrier_nco": carrier_nco,
        "code_err": code_err,
        "code_nco": code_nco,
        "samples": samples,
        "samples_biased": samples_biased,
        "carrier_phase": np.array(tb.cordic_sincos.past_inputs),
        "carrier_out": np.array(tb.cordic_sincos.past_outputs),
        "carr_freq": carr_freq,
        "code_freq_offset": code_freq_offset,
    }

    with open("data.pickle", "wb") as f:
        pickle.dump(save_data, f)

    graph.main(True)


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="TrackingChannel",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
        verilog_sources=["hw/verilog/CordicSinCos.v", "hw/verilog/CordicAtan.v"],
    )
