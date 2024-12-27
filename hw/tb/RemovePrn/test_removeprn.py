#!/usr/bin/env python

import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout

import numpy as np
import matplotlib.pyplot as plt
from gps import prn_gen

import fpga_utils.spinal_stream as stream
from fpga_utils import (
    corr,
    dsp,
    gps_sim,
    TbTemplate,
    test_runner,
)


class TB(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        self.input = stream.SpinalStreamSource.from_prefix(dut, "io_input")
        self.output = stream.SpinalStreamSink.from_prefix(dut, "io_output")

        self.dut.io_sv.value = 0
        self.dut.io_set.value = 0
        self.dut.io_phase_offset.value = 0

    # Simulate sample rate
    def iq_pause(self, f=50, fs=4.092):
        x = 0

        while True:
            x += 1 / f

            if x > 1 / fs:
                x -= 1 / fs
                yield False
            else:
                yield True

    async def send_data(self, data):
        await self.input.send(data)
        await self.input.wait()

    async def configure(self, sv: int = 1, offset: int = 0):
        self.dut.io_sv.value = sv - 1
        self.dut.io_phase_offset.value = offset
        self.dut.io_set.value = 1
        await ClockCycles(self.dut.clk, 1)
        self.dut.io_set.value = 0
        await ClockCycles(self.dut.clk, 1)

    async def run_test(
        self, offset=0, timestamp_offset=0, cycles=2, gps_data=True, slow=False
    ):
        if slow:
            # Doesn't have to be correct fs, just slower than main clock
            self.input.set_pause_generator(self.iq_pause(fs=10))
        else:
            self.input.clear_pause_generator()

        await self.configure(offset=offset)

        count = int(cycles * 4096)

        if gps_data:
            samples = gps_sim.generate_gps(
                f_s=4.092e6,
                n=count,
                sv=1,
                sample_phase=offset,
                signal_power=-128.5,
            )
        else:
            samples = np.ones(count, dtype=np.complex64)

        samples *= 3 / 4 * 127
        samples_re, samples_im = dsp.to_2b(samples)
        samples_quant = dsp.quantize_2b(samples_re, samples_im)
        data = {
            "c_re": samples_re,
            "c_im": samples_im,
            "t": dsp.generate_timestamp(len(samples), offset=timestamp_offset),
        }

        # Send samples
        await with_timeout(self.send_data(data), 1500000, "ns")
        # Extra delay to allow pipeline to finish
        await ClockCycles(self.dut.clk, 20)

        # Receive data
        actual = await with_timeout(self.output.read(), 150000, "ns")
        early_sim = np.array(actual.payload["0_re"]).astype(np.int8) + 1j * np.array(
            actual.payload["0_im"]
        ).astype(np.int8)
        prompt_sim = np.array(actual.payload["1_re"]).astype(np.int8) + 1j * np.array(
            actual.payload["1_im"]
        ).astype(np.int8)
        late_sim = np.array(actual.payload["2_re"]).astype(np.int8) + 1j * np.array(
            actual.payload["2_im"]
        ).astype(np.int8)

        # Reference data
        prn_data = prn_gen.sample(
            1, 4.092e6, cycles * 4096, offset_samples=offset + timestamp_offset
        )
        early_ref = samples_quant * np.roll(prn_data, -1)
        prompt_ref = samples_quant * np.roll(prn_data, 0)
        late_ref = samples_quant * np.roll(prn_data, 1)

        # Get correct offset
        dropped = int(self.dut.io_dropped.value)
        early_ref = early_ref[dropped:]
        prompt_ref = prompt_ref[dropped:]
        late_ref = late_ref[dropped:]

        if len(early_ref) > len(early_sim):
            early_ref = early_ref[: len(early_sim)]
            prompt_ref = prompt_ref[: len(prompt_sim)]
            late_ref = late_ref[: len(late_sim)]
        else:
            early_sim = early_sim[: len(early_ref)]
            prompt_sim = prompt_sim[: len(prompt_ref)]
            late_sim = late_sim[: len(late_ref)]

        early_corr = corr(early_ref, early_sim)
        prompt_corr = corr(prompt_ref, prompt_sim)
        late_corr = corr(late_ref, late_sim)

        self.dut._log.info(
            f"IQ offset {offset}, timestamp offset {timestamp_offset}, early_corr={early_corr:0.3f}, prompt_corr={prompt_corr:0.3f}, late_corr={late_corr:0.3f}, count={len(prompt_ref)}"
        )

        if early_corr < 0.99 or prompt_corr < 0.99 or late_corr < 0.99:
            plt.figure(figsize=(8, 6), dpi=300)

            plt.subplot(2, 1, 1)
            plt.title("Reference")
            plt.plot(early_ref.real, lw=1.5, label="Early")
            plt.plot(prompt_ref.real, lw=1, label="Prompt")
            plt.plot(late_ref.real, lw=0.5, label="Late")
            plt.grid()
            plt.legend()
            plt.xlim([0, 25])

            plt.subplot(2, 1, 2)
            plt.title("Simulation")
            plt.plot(early_sim.real, lw=1.5)
            plt.plot(prompt_sim.real, lw=1)
            plt.plot(late_sim.real, lw=0.5)
            plt.grid()
            plt.xlim([0, 25])

            plt.tight_layout()
            plt.savefig("comparison.png")

        assert early_corr > 0.99
        assert prompt_corr > 0.99
        assert late_corr > 0.99
        assert len(early_sim) > 3000


@cocotb.test()
async def test_dut(dut):
    tb = TB(dut)

    await tb.reset()

    await tb.run_test(0, 0, gps_data=False, slow=True)
    await tb.run_test(0, 0, gps_data=False, slow=False)
    await tb.run_test(123, 321, gps_data=False, slow=False)
    await tb.run_test(456, 654, gps_data=True, slow=False)
    await tb.run_test(789, 987, gps_data=True, slow=True)

    for phase_offset in [0, 10, 3910, 4091]:
        for iq_offset in [0, 5, 4050]:
            await tb.run_test(phase_offset, iq_offset, slow=False)
            await tb.run_test(phase_offset, iq_offset, slow=True)


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="RemovePrn",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
        # verilog_sources=["hw/verilog/CordicSinCos.v", "hw/verilog/CordicAtan.v"],
    )
