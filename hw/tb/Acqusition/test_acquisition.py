import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotbext import axi

import matplotlib.pyplot as plt
import numpy as np
import logging
from gps import gps_sim, prn

import sys
from pathlib import Path

# Hack to share fft_sim between multiple tests
fft_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(fft_path.resolve()))

from fft_sim import FFT_Sim, pack_complex, unpack_complex

class TB:
    def __init__(self, dut, period=20, fs=4.092e6) -> None:
        self.dut = dut
        self.fs = fs

        self._sim = FFT_Sim(dut.fft_inst, 12, 1, store=True)

        # Clock
        cocotb.start_soon(Clock(self.dut.clk, period, "ns").start())

        # Sample input
        bus = axi.AxiStreamBus(self.dut)
        bus._add_signal("tdata", "io_iq_payload")
        bus._add_signal("tvalid", "io_iq_valid")
        bus._add_signal("tready", "io_iq_ready")
        self.sample_input = axi.AxiStreamSource(bus, dut.clk, byte_size=16)
        self.sample_input.log.setLevel(logging.WARNING) # Get rid of log messages

    def send_samples(self, count=1e5, sv=1, doppler=0, sample_phase=0, noise=True):
        power = -125 if noise else None

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
    tb = TB(dut)
    log = dut._log

    await tb.reset()

    ref_phase = 2346
    tb.send_samples(sample_phase=ref_phase, noise=True)

    await ClockCycles(dut.clk, 80000)

    result_freq = dut.fsm_max_freq.value.signed_integer
    result_phase = dut.fsm_max_idx.value.integer
    log.info(f"Frequency bin: {result_freq}, code sample offset: {result_phase}")

    # Analyze FFT results
    inputs = tb._sim.past_inputs
    outputs = tb._sim.past_outputs

    # Check samples
    samples_ref = tb.samples[16:16+4096]
    # samples_ref = tb.samples[0:4096]

    samples_ref_in = inputs[0][0]
    samples_fft = outputs[0][0]
    ref_fft = np.fft.fft(samples_ref / 127)

    # Check PRN
    prn_ref = prn.sample(1, 4.092e6, 4096)
    prn_ref_fft = np.fft.fft(prn_ref / 127)
    prn_in = inputs[1][0]
    prn_out = outputs[1][0]

    # Check mix
    ref_mix = ref_fft.conj() * prn_ref_fft
    out_mix = samples_fft.conj() * prn_out

    # out = outputs[2][0] * (2**outputs[2][1])

    plt.figure(figsize=(12, 12), dpi=150)

    plt.subplot(4, 2, 1)
    plt.plot(np.abs(ref_fft))
    plt.title("Reference Sample FFT")

    plt.subplot(4, 2, 2)
    plt.plot(np.abs(samples_fft))
    plt.title("Simulated Sample FFT")

    plt.subplot(4, 2, 3)
    plt.plot(np.abs(prn_ref_fft))
    plt.title("Reference PRN FFT")

    plt.subplot(4, 2, 4)
    plt.plot(np.abs(prn_out))
    plt.title("Simulated PRN FFT")

    plt.subplot(4, 2, 5)
    plt.plot(np.abs(ref_mix))
    plt.title("Reference Mixed FFT")

    plt.subplot(4, 2, 6)
    plt.plot(np.abs(out_mix))
    plt.title("Simulated Mixed FFT")

    plt.subplot(4, 2, 7)
    ref_mix_ifft = np.abs(np.fft.ifft(ref_mix))
    phase_est = np.argmax(ref_mix_ifft)
    plt.plot(ref_mix_ifft)
    plt.title(f"Reference Mixed IFFT {phase_est}, {ref_mix_ifft[phase_est]/np.mean(ref_mix_ifft):.3f}")

    plt.subplot(4, 2, 8)
    out_mix_ifft = np.abs(np.fft.ifft(out_mix))
    out_phase_est = np.argmax(out_mix_ifft)
    plt.plot(out_mix_ifft)
    plt.title(f"Simulated Mixed IFFT {out_phase_est}, {out_mix_ifft[out_phase_est]/np.mean(out_mix_ifft):.3f}")

    plt.tight_layout()
    plt.savefig("results.png")

    # Actual mix
    num = 5

    plt.figure(figsize=(15, 12), dpi=150)

    for i in range(num):
        in_fft = inputs[2+i][0]
        out = outputs[2+i][0]
        out_exp = outputs[2+i][1]

        plt.subplot(num, 3, 1+3*i)
        plt.plot(np.abs(in_fft))
        plt.title(f"In {i}, {np.mean(in_fft):.4f}")

        plt.subplot(num, 3, 2+3*i)
        plt.plot(np.abs(out))
        plt.title(f"Out {i}, {out_exp}")

        plt.subplot(num, 3, 3+3*i)
        plt.plot(np.abs(np.fft.ifft(in_fft)))
        plt.title("IFFT(In)")

    plt.tight_layout()
    plt.savefig("mixed.png")

    # Do assertions after graphing

    corr = np.correlate(ref_fft, samples_fft, mode="full")
    assert np.argmax(np.abs(corr)) == 4095, np.argmax(np.abs(corr))

    corr = np.correlate(prn_ref_fft, prn_out, mode="full")
    assert np.argmax(np.abs(corr)) == 4095, np.argmax(np.abs(corr))

    corr = np.correlate(np.abs(ref_mix), np.abs(out_mix), mode="full")
    assert np.argmax(np.abs(corr)) == 4095, np.argmax(np.abs(corr))

    assert result_phase == ref_phase, f"{result_phase}, {ref_phase}"

