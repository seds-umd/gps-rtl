import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotbext import axi

import matplotlib.pyplot as plt
import numpy as np
import logging
import itertools
from gps import gps_sim, prn

import sys
from pathlib import Path

# Hack to share fft_sim between multiple tests
fft_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(fft_path.resolve()))

from fft_sim import FFT_Sim, pack_complex, unpack_complex
from utils import corr, random_pause

class TB:
    def __init__(self, dut, period=20, fs=4.092e6) -> None:
        self.dut = dut
        self.fs = fs

        self.fft_sim = FFT_Sim(dut.fft_inst, 12, 1, store=True)

        # Clock
        cocotb.start_soon(Clock(self.dut.clk, period, "ns").start())

        # Sample input
        bus = axi.AxiStreamBus(self.dut)
        bus._add_signal("tdata", "io_iq_payload")
        bus._add_signal("tvalid", "io_iq_valid")
        bus._add_signal("tready", "io_iq_ready")
        self.sample_input = axi.AxiStreamSource(bus, dut.clk, byte_size=16)
        self.sample_input.log.setLevel(logging.WARNING) # Get rid of log messages

        # self.sample_input.set_pause_generator(random_pause())

    def send_samples(self, count=1e5, sv=1, doppler=0, sample_phase=0, noise=True):
        power = -120 if noise else None

        if noise:
            self.dut._log.info(f"Noise power set to {power} dBm")
        else:
            self.dut._log.info("Noise disabled")

        # 3/4 is about optimal for 33% magnitude bit density (per MAX2769 datasheet)
        self.samples = 3/4 * 127 * gps_sim.generate_gps(self.fs, int(count), sv, doppler, sample_phase=sample_phase, signal_power=power)
        timestamp = np.tile(np.arange(4092), int(len(self.samples)/4092)+1).astype(np.uint16)[0:len(self.samples)]

        # Convert to 4 bit format
        samples_re = self.samples.real.astype(np.int8).astype(np.uint8) >> 6
        samples_im = self.samples.imag.astype(np.int8).astype(np.uint8) >> 6
        bits = samples_re | (samples_im << 2) | (timestamp << 4)
        bits = [int(x) for x in bits]

        self.sample_input.send_nowait(bits)

    async def reset(self):
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 0

@cocotb.test()
async def test_acquisition(dut):
    # Threshold for correlation
    CORR_THRES = 0.5

    tb = TB(dut)
    log = dut._log

    await tb.reset()

    ref_phase = 0 # out of 4096, code will start at this index (ahead of zero)
    doppler = 750 # Hz
    sample_phase = ref_phase - 4 if ref_phase >= 4096/2 else ref_phase # out of 4092
    tb.send_samples(doppler=doppler, sample_phase=sample_phase, noise=True)

    log.info(f"Sending samples with doppler shift of {doppler} Hz and phase offset of {sample_phase}")

    await ClockCycles(dut.clk, 120000)

    result_freq = dut.fsm_max_freq.value.signed_integer
    result_phase = dut.fsm_max_idx.value.integer
    log.info(f"Results: frequency bin = {result_freq}, sample offset = {result_phase}")

    # Get inputs and output of FFT module
    inputs = tb.fft_sim.past_inputs
    outputs = tb.fft_sim.past_outputs

    # Each check step below will use the results of the previous step as the
    # reference so the error represents that step alone instead of carrying
    # error forward.

    # Check samples
    samples = tb.samples[0:4096]
    samples_ref = inputs[0][0]
    samples_corr = corr(samples, samples_ref)
    log.info(f"Samples correlation: {samples_corr:0.3f}")

    # Check FFT
    samples_fft = outputs[0][0]
    ref_fft = np.fft.fft(samples)
    fft_corr = corr(samples_fft, ref_fft)
    log.info(f"Initial FFT correlation: {fft_corr:0.3f}")
    assert fft_corr > CORR_THRES

    # Check PRN
    prn_ref = prn.sample(1, 4.092e6, 4096)
    prn_in = inputs[1][0]
    prn_corr = corr(prn_ref, prn_in)
    log.info(f"PRN correlation: {prn_corr:0.3f}")
    assert prn_corr > CORR_THRES

    # Check PRN FFT
    prn_ref_fft = np.fft.fft(prn_in)
    prn_fft = outputs[1][0]
    prn_fft_corr = corr(prn_ref_fft, prn_fft)
    log.info(f"PRN FFT correlation: {prn_fft_corr:0.3f}")
    assert prn_fft_corr > CORR_THRES

    # Check mix
    # The testbench uses a frequency shift of +-1 bin and starts at the
    # most negative frequency. np.roll shift is negative of the real shift
    ref_mix = samples_fft.conj() * np.roll(prn_fft, 1)
    sim_mix = inputs[2][0]
    mix_corr = corr(ref_mix, sim_mix)
    log.info(f"Mix correlation: {mix_corr:0.3f}")
    assert mix_corr > CORR_THRES

    # Check IFFT of mix
    ref_mix_ifft = np.fft.ifft(sim_mix)
    log.info(f"Mix IFFT peak: {np.argmax(np.abs(ref_mix_ifft))}")

    # Check fine acquisition
    for fine2_offset in range(4090, 4120):
        # fine2_offset = 4093 # offset at start of fine2 state
        start_idx = 4092 + fine2_offset
        end_idx = start_idx + 8*4096

        pre_dec_samples_ref = tb.samples[start_idx:end_idx]
        pre_dec_prn_ref = prn.sample(1, 4.092e6, 4096*8, offset_samples=fine2_offset+ref_phase)
        pre_dec_mixed = pre_dec_samples_ref * pre_dec_prn_ref
        dec_samples_ref = np.sum(pre_dec_mixed.reshape(-1, 8), axis=1) / 8
        dec_samples = inputs[-1][0]
        # dec_fft = outputs[-1][0]

        dec_mixed_corr = corr(dec_samples_ref, dec_samples)
        log.info(f"{fine2_offset} Dec/mix correlation: {dec_mixed_corr:0.3f}")

    # plt.figure()
    # plt.subplot(2, 1, 1)
    # plt.plot(np.abs(dec_samples_ref))
    # plt.xlim([0, 200])
    # plt.subplot(2, 1, 2)
    # plt.plot(np.abs(dec_samples))
    # plt.xlim([0, 200])
    # plt.savefig("fine_compare.png")

    # dec_fft_ref = np.fft.fft(dec_samples_ref)
    # dec_fft_corr = corr(dec_fft_ref, dec_fft)
    # log.info(f"Dec FFT correlation: {dec_fft_corr:0.3f}")

    # plt.figure()
    # plt.plot(np.abs(dec_fft))
    # plt.tight_layout()
    # plt.savefig("fine.png")
    # log.info(f"Fine acquisition peak at {np.argmax(dec_fft)}")

    # Do assertions after graphing

    # corr = np.correlate(ref_fft, samples_fft, mode="full")
    # assert np.argmax(np.abs(corr)) == 4095, np.argmax(np.abs(corr))

    # corr = np.correlate(prn_ref_fft, prn_out, mode="full")
    # assert np.argmax(np.abs(corr)) == 4095, np.argmax(np.abs(corr))

    # corr = np.correlate(np.abs(ref_mix), np.abs(out_mix), mode="full")
    # assert np.argmax(np.abs(corr)) == 4095, np.argmax(np.abs(corr))

    assert result_phase == ref_phase, f"{result_phase}, {ref_phase}"
