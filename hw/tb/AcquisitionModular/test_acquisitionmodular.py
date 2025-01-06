#!/usr/bin/env python

import cocotb
from cocotb.triggers import ClockCycles, RisingEdge, with_timeout

import matplotlib.pyplot as plt
import numpy as np
import logging

import fpga_utils
import fpga_utils.spinal_stream as stream
from fpga_utils import test_runner
from fpga_utils.fft_sim import FFT_Sim
from gps import prn_gen
from gps.gps import acquisition


CORR_THRESHOLD = 0.99


class TB(fpga_utils.TbTemplate):
    def __init__(self, dut, period=20, fs=4.092e6) -> None:
        super().__init__(dut, period=period)
        self.fs = fs

        self.sample_input = stream.SpinalStreamSource.from_prefix(dut, "io_iq")
        self.results_bus = stream.SpinalStreamSink.from_prefix(dut, "io_results")

        self.fft_sim = FFT_Sim(dut.fft_inst, 12, 1, store=True)
        self.fft_sim.log.setLevel(logging.WARNING)

        # Commented out to speed up tests
        # self.sample_input.set_pause_generator(random_pause())

    def send_generated_samples(
        self, count=1e5, sv=1, doppler=0, sample_phase=0, noise=True
    ):
        # -128.5 is worst case real world received power
        power = -128.5 if noise else None

        if noise:
            self.dut._log.info(f"Noise power set to {power} dBm")
        else:
            self.dut._log.info("Noise disabled")

        self.sample_bits, self.samples, self.samples_quant = (
            fpga_utils.generate_gps_samples(
                self.fs, count, sv, doppler, sample_phase, power
            )
        )

        self.sample_input.send_nowait(self.sample_bits)

    def send_file_samples(self, file="", data_type=np.int8, count=1e5):
        data = np.fromfile(file, dtype=data_type, count=int(count))

        samples = data[::2].astype(np.complex64) + 1j * data[1::2].astype(np.complex64)

        # Normalize - scaling optimized for SNR
        samples /= np.max(np.abs(samples))
        samples *= 127

        # Repeat
        times_single = np.arange(4092)
        times = np.tile(times_single, int(len(samples) / 4092) + 1)
        times = times.astype(np.uint16)[0 : len(samples)]

        # Convert to 4 bit format
        samples_re = samples.real.astype(np.int8).astype(np.uint8) >> 6
        samples_im = samples.imag.astype(np.int8).astype(np.uint8) >> 6
        bits = samples_re | (samples_im << 2) | (times << 4)
        bits = [int(x) for x in bits]

        # Get quantized samples
        samples_re = (samples_re << 6).astype(np.int8) | 0b100000
        samples_im = (samples_im << 6).astype(np.int8) | 0b100000

        samples_quant = samples_re + samples_im * 1j
        samples_quant /= 128

        self.sample_bits = bits
        self.samples = samples
        self.samples_quant = samples_quant

        self.sample_input.send_nowait(self.sample_bits)

    async def wait_for_state(self, state: str):
        curr_state = self.dut.fsm_stateReg_string

        while state.lower().strip() != curr_state.value.buff.decode().lower().strip():
            await ClockCycles(self.dut.clk, 1)

    async def get_results(self, timeout=1e7):
        self.dut.io_results_ready.value = 1

        if self.dut.io_results_valid.value == 0:
            await with_timeout(RisingEdge(self.dut.io_results_valid), timeout, "ns")
            await RisingEdge(self.dut.clk)

        res = self.results_bus.read_nowait()
        # TODO: need to add signed int support to stream bus to be able to use it here

        sv = res.payload["sv"][0]
        freq_offset = self.dut.io_results_payload_freq_offset.value.signed_integer
        phase_offset = res.payload["phase_offset"][0]
        snr = res.payload["snr"][0]

        return sv, freq_offset, phase_offset, snr


def graph_samples(samples, filename):
    plt.figure(figsize=(8, 6), dpi=300)
    plt.plot(samples.real)
    plt.plot(samples.imag)
    plt.tight_layout()
    plt.savefig(filename)


def shift_saturate(samples, bits):
    samples = samples * (1 << bits)
    samples.real = np.clip(samples.real, -1, 1)
    samples.imag = np.clip(samples.imag, -1, 1)

    return samples


@cocotb.test(skip=True)
async def looped_test(dut):
    tb = TB(dut)

    await tb.reset()

    tb.send_generated_samples(count=5e6, sv=2, doppler=100, sample_phase=100)

    # Run through all of the SVs
    for _ in range(32):
        await with_timeout(tb.wait_for_state("prn_in"), 2000 * 1000, "ns")
        await with_timeout(tb.wait_for_state("calc_snr"), 2000 * 1000, "ns")

        results = await tb.get_results(1e3)
        print(results)


@cocotb.test(skip=False)
async def correlation_test(dut, freq_span=2):
    np.random.seed(785498247)
    tb = TB(dut)
    log = dut._log

    await tb.reset()

    # out of 4096, code will start at this index (ahead of zero)
    ref_phase = np.random.randint(4096)

    sv = 1

    freq_bin_size = 4096 / 4.092
    doppler = np.random.uniform(-freq_span * freq_bin_size, freq_span * freq_bin_size)

    expected_coarse_freq = int(np.round(doppler / freq_bin_size))
    expected_fine_freq = int(np.round(8 * doppler / freq_bin_size))

    sample_phase = int(np.round(ref_phase * 4092 / 4096))

    tb.send_generated_samples(
        count=5e6, sv=sv, doppler=doppler, sample_phase=sample_phase, noise=True
    )

    log.info(f"Shift: {doppler:0.1f} Hz, Phase: {sample_phase}")

    # Run until coarse acquisition is done
    await with_timeout(tb.wait_for_state("fine_setup"), 2000 * 1000, "ns")

    # Get inputs and output of FFT module
    inputs = tb.fft_sim.past_inputs
    outputs = tb.fft_sim.past_outputs

    # Check quantization (before anything is actually simulated)
    ref_quant = tb.samples_quant[:4096]
    ref_quant_corr = fpga_utils.corr(tb.samples[:4096], tb.samples_quant[:4096])
    log.info(f"Reference to quantized samples correlation: {ref_quant_corr:0.3f}")
    # Lower correlation is expected, some information is lost here since we go from float32 to 2 bit int
    assert ref_quant_corr > 0.4

    sample_in_corr = fpga_utils.corr(tb.samples_quant[:4096], inputs[0][0])
    log.info(f"Sample input to FFT input correlation: {sample_in_corr:0.3f}")
    assert sample_in_corr > CORR_THRESHOLD

    # Check FFT output
    fft_expected = np.fft.fft(ref_quant)
    fft_actual = shift_saturate(outputs[0][0], 2)
    fft_corr = fpga_utils.corr(fft_expected, fft_actual)
    log.info(f"FFT correlation: {fft_corr:0.3f}")
    assert fft_corr > CORR_THRESHOLD

    # Check PRN - always starts with first SV
    prn_expected = prn_gen.sample(1, 4.092e6, 4096)
    prn_actual = inputs[1][0]
    prn_corr = fpga_utils.corr(prn_expected, prn_actual)
    log.info(f"PRN correlation: {prn_corr:0.3f}")
    assert prn_corr > CORR_THRESHOLD

    # Check PRN FFT
    prn_fft_expected = np.fft.fft(prn_expected)
    prn_fft_actual = shift_saturate(outputs[1][0], 1)
    prn_fft_corr = fpga_utils.corr(prn_fft_expected, prn_fft_actual)
    log.info(f"PRN FFT correlation: {prn_fft_corr:0.3f}")
    assert prn_fft_corr > CORR_THRESHOLD

    # Check mix
    # The testbench uses a frequency shift of +-1 bin and starts at the
    # most negative frequency. np.roll shift is negative of the real shift
    mix_expected = fft_actual.conj() * np.roll(prn_fft_actual, -2)
    mix_actual = inputs[2][0]
    mix_corr = fpga_utils.corr(mix_expected, mix_actual)
    log.info(f"Mix correlation: {mix_corr:0.3f}")
    # TODO: figure out why this check doesn't work

    # Run fine acquisition
    await with_timeout(tb.wait_for_state("calc_snr"), 2000 * 1000, "ns")

    # Check results
    results = await tb.get_results(1e3)

    result_coarse_freq = dut.coarse_freq.value.signed_integer
    result_fine_freq = results[1]
    result_phase = results[2]

    log.info(
        f"Coarse frequency expected: {expected_coarse_freq}, actual: {result_coarse_freq}"
    )
    log.info(
        f"Fine frequency expected: {expected_fine_freq}, actual: {result_fine_freq}"
    )
    log.info(f"Phase expected: {sample_phase}, actual: {result_phase}")
    log.info(f"Calculated SNR: {results[3]}")

    # Allow error of +- 1
    assert abs(result_coarse_freq - expected_coarse_freq) < 2
    assert abs(result_phase - sample_phase) < 2
    assert abs(result_fine_freq - expected_fine_freq) < 2


async def test_single(dut, freq_span=2):
    tb = TB(dut)
    log = dut._log

    await tb.reset()

    ref_phase = np.random.randint(4096)

    freq_bin_size = 4096 / 4.092
    doppler = np.random.uniform(-freq_span * freq_bin_size, freq_span * freq_bin_size)

    expected_coarse_freq = int(np.round(doppler / freq_bin_size))
    expected_fine_freq = int(np.round(8 * doppler / freq_bin_size))

    sample_phase = int(np.round(ref_phase * 4092 / 4096))

    tb.send_generated_samples(doppler=doppler, sample_phase=sample_phase, noise=True)

    # Run until coarse acquisition is done
    await with_timeout(tb.wait_for_state("fine_setup"), 2000 * 1000, "ns")

    # Check result
    result_coarse_freq = dut.coarse_freq.value.signed_integer
    result_phase = dut.phase_offset.value.integer
    assert result_coarse_freq == expected_coarse_freq
    assert abs(result_phase - sample_phase) < 2

    # Run fine acquisition
    await with_timeout(tb.wait_for_state("calc_snr"), 2000 * 1000, "ns")

    result_fine_freq = dut.fine_freq.value.signed_integer
    assert result_fine_freq == expected_fine_freq, f"Expected {expected_fine_freq}"

    # Check result stream
    results = await tb.get_results(1e3)
    assert results[1] == expected_fine_freq


@cocotb.test(skip=True)
async def statistical_test(dut):
    N = 1
    success = 0

    for _ in range(N):
        try:
            await test_single(dut)
            success += 1
        except AssertionError:
            dut._log.warning(f"Failed")
            continue

    dut._log.info(f"{success}/{N} passed")


@cocotb.test(skip=True)
async def recorded_sample_test(dut):
    # cwd is sim_build
    file = "../../../../../gps-model/data/1/gpssim.ci16"

    tb = TB(dut)
    log = dut._log
    await tb.reset()

    log.info(f"Loading samples from {file}")
    tb.send_file_samples(file, data_type=np.int8, count=5e7)

    expected_svs = []

    for i in range(32 * 8):
        if i % 32 == 0:
            expected = acquisition(
                tb.samples_quant[i * 4092 * (1 + 8) :], 4.092e6, 10e3, 1000
            )
            for res in expected:
                expected_svs.append(res[0])
                log.info(
                    f"Python: sv={res[0]}, shift={res[1]:.0f}, phase={res[2]}, snr={res[3]:.2f}"
                )

        res = await with_timeout(tb.get_results(), 4, "ms")

        if res[3] > 8:
            log.info(
                f"RTL: sv={res[0]}, shift={res[1] * 4096 / 4.092 / 8:.0f}, phase={res[2]}, snr={res[3]}"
            )

        await ClockCycles(dut.clk, 10)


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="AcquisitionModular",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
        verilog_sources=["hw/verilog/XilinxFFT.v"],
    )
