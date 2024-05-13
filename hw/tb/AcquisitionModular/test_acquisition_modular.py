import cocotb
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import matplotlib.pyplot as plt
import numpy as np
from gps import gps_sim, prn

import sys
from pathlib import Path

# Hack to share fft_sim between multiple tests
utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from fft_sim import FFT_Sim, pack_complex, unpack_complex
from utils import TB_Template, corr, random_pause, axis_source, generate_gps_samples

CORR_THRESHOLD = 0.99


class TB(TB_Template):
    def __init__(self, dut, period=20, fs=4.092e6) -> None:
        super().__init__(dut, period)
        self.fs = fs

        self.sample_input = axis_source(dut, "io_iq_", byte_size=16)

        self.fft_sim = FFT_Sim(dut.fft_inst, 12, 1, store=True)

        # self.sample_input.set_pause_generator(random_pause())

    def send_samples(self, count=1e5, sv=1, doppler=0, sample_phase=0, noise=True):
        power = -120 if noise else None

        if noise:
            self.dut._log.info(f"Noise power set to {power} dBm")
        else:
            self.dut._log.info("Noise disabled")

        self.sample_bits, self.samples, self.samples_quant = generate_gps_samples(
            self.fs, count, sv, doppler, sample_phase, power
        )

        self.sample_input.send_nowait(self.sample_bits)

    async def wait_state(self, state: str):
        curr_state = self.dut.fsm_stateReg_string

        while state.lower().strip() != curr_state.value.buff.decode().lower().strip():
            await ClockCycles(self.dut.clk, 1)


def graph_samples(samples, filename):
    plt.figure(figsize=(6, 4), dpi=300)
    plt.plot(samples.real)
    plt.plot(samples.imag)
    plt.tight_layout()
    plt.savefig(filename)


def shift_saturate(samples, bits):
    samples = samples * (1 << bits)
    samples.real = np.clip(samples.real, -1, 1)
    samples.imag = np.clip(samples.imag, -1, 1)

    return samples


@cocotb.test()
async def test_acquisition(dut):
    tb = TB(dut)
    log = dut._log

    await tb.reset()

    # out of 4096, code will start at this index (ahead of zero)
    ref_phase = np.random.randint(4096)
    doppler = 750  # Hz
    sample_phase = ref_phase - 4 if ref_phase >= 4096 / 2 else ref_phase  # out of 4092
    tb.send_samples(doppler=doppler, sample_phase=sample_phase, noise=True)

    log.info(f"Shift: {doppler} Hz, Phase: {sample_phase}")

    # Run until coarse acquisition is done
    await with_timeout(tb.wait_state("evaluate"), 1000000, "ns")

    # Get inputs and output of FFT module
    inputs = tb.fft_sim.past_inputs
    outputs = tb.fft_sim.past_outputs

    # Check quantization (before anything is actually simulated)
    ref_quant = tb.samples_quant[:4096]
    ref_quant_corr = corr(tb.samples[:4096], tb.samples_quant[:4096])
    log.info(f"Reference to quantized correlation: {ref_quant_corr:0.3f}")
    assert ref_quant_corr > 0.4  # Some information is lost here

    sample_in_corr = corr(tb.samples_quant[:4096], inputs[0][0])
    log.info(f"Sample input to FFT input correlation: {sample_in_corr:0.3f}")
    assert sample_in_corr > CORR_THRESHOLD

    # Check FFT output
    fft_expected = np.fft.fft(ref_quant)
    fft_actual = shift_saturate(outputs[0][0], 2)
    fft_corr = corr(fft_expected, fft_actual)
    log.info(f"FFT correlation: {fft_corr:0.3f}")
    assert fft_corr > CORR_THRESHOLD

    # Check PRN
    prn_expected = prn.sample(1, 4.092e6, 4096)
    prn_actual = inputs[1][0]
    prn_corr = corr(prn_expected, prn_actual)
    log.info(f"PRN correlation: {prn_corr:0.3f}")
    assert prn_corr > CORR_THRESHOLD

    # Check PRN FFT
    prn_fft_expected = np.fft.fft(prn_expected)
    prn_fft_actual = shift_saturate(outputs[1][0], 1)
    prn_fft_corr = corr(prn_fft_expected, prn_fft_actual)
    log.info(f"PRN FFT correlation: {prn_fft_corr:0.3f}")
    assert prn_fft_corr > CORR_THRESHOLD

    # Check mix
    # The testbench uses a frequency shift of +-1 bin and starts at the
    # most negative frequency. np.roll shift is negative of the real shift
    mix_expected = fft_actual.conj() * np.roll(prn_fft_actual, -1)
    mix_actual = inputs[2][0]
    mix_corr = corr(mix_expected, mix_actual)
    log.info(f"Mix correlation: {mix_corr:0.3f}")

    # Check result
    result_freq = dut.max_mag_io_max_freq.value.signed_integer
    result_phase = dut.max_mag_io_max_idx.value.integer
    log.info(f"Output: frequency={result_freq}, phase={result_phase}")
    # assert result_freq ==
    assert result_phase == ref_phase
