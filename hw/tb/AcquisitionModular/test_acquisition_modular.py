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
from utils import TB_Template, corr, random_pause, axis_source


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

        # 3/4 is about optimal for 33% magnitude bit density (per MAX2769 datasheet)
        self.samples = (3 / 4 * 127) * gps_sim.generate_gps(
            f_s=self.fs,
            n=int(count),
            sv=sv,
            doppler=doppler,
            sample_phase=sample_phase,
            signal_power=power,
        )
        timestamp = np.tile(np.arange(4092), int(len(self.samples) / 4092) + 1)
        timestamp = timestamp.astype(np.uint16)[0 : len(self.samples)]

        # Convert to 4 bit format
        samples_re = self.samples.real.astype(np.int8).astype(np.uint8) >> 6
        samples_im = self.samples.imag.astype(np.int8).astype(np.uint8) >> 6
        bits = samples_re | (samples_im << 2) | (timestamp << 4)
        bits = [int(x) for x in bits]

        self.sample_input.send_nowait(bits)

        # Get quantized samples
        samples_re = (samples_re << 6).astype(np.int8) | 0b100000
        samples_im = (samples_im << 6).astype(np.int8) | 0b100000

        self.samples_quant = samples_re + samples_im * 1j
        self.samples_quant /= 128

    async def wait_state(self, state: str):
        curr_state = self.dut.fsm_stateReg_string

        while state.lower().strip() != curr_state.value.buff.decode().lower().strip():
            await ClockCycles(self.dut.clk, 1)


@cocotb.test()
async def test_acquisition(dut):
    tb = TB(dut)
    log = dut._log

    await tb.reset()

    ref_phase = 0  # out of 4096, code will start at this index (ahead of zero)
    doppler = 750  # Hz
    sample_phase = ref_phase - 4 if ref_phase >= 4096 / 2 else ref_phase  # out of 4092
    tb.send_samples(doppler=doppler, sample_phase=sample_phase, noise=True)

    log.info(f"Shift: {doppler} Hz, Phase: {sample_phase}")

    # await ClockCycles(dut.clk, 10000)
    await with_timeout(tb.wait_state("shift_mix"), 1000000, "ns")

    # Get inputs and output of FFT module
    inputs = tb.fft_sim.past_inputs
    outputs = tb.fft_sim.past_outputs

    # Check quantization (before anything is actually simulated)
    ref_quant = tb.samples_quant[:4096]
    ref_quant_corr = corr(tb.samples[:4096], tb.samples_quant[:4096])
    log.info(f"Reference to quantized correlation: {ref_quant_corr:0.3f}")

    sample_in_corr = corr(tb.samples_quant[:4096], inputs[0][0])
    log.info(f"Sample input to FFT input correlation: {sample_in_corr:0.3f}")

    # Check FFT output
    fft_expected = np.fft.fft(ref_quant)
    fft_actual = outputs[0][0]
    fft_corr = corr(fft_expected, fft_actual)
    log.info(f"FFT correlation: {fft_corr:0.3f}")
