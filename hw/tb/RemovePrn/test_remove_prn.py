import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path
from gps import prn_gen as prn

from fpga_utils.fft_sim import fft_unpack_complex as unpack_complex
from fpga_utils import TbTemplate, axis_sink, axis_source, corr, generate_gps_samples


class TB(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        self.input = axis_source(dut, "io_input_", byte_size=16)
        self.output = axis_sink(dut, "io_output_", byte_size=16)
        self.input.set_pause_generator(self.iq_pause())

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

    async def get_data(self):
        frame: axi.AxiStreamFrame = await self.output.read()

        return frame

    async def configure(self, sv: int = 1, offset: int = 0):
        self.dut.io_sv.value = sv - 1
        self.dut.io_phase_offset.value = offset
        self.dut.io_set.value = 1
        await ClockCycles(self.dut.clk, 1)
        self.dut.io_set.value = 0
        await ClockCycles(self.dut.clk, 1)

    async def run_test(self, offset=0, timestamp_offset=0, cycles=1):
        await self.configure(offset=offset)
        self.output.read_nowait()

        bits, samples, quant = generate_gps_samples(
            4.092e6, cycles * 4096, 1, 0, offset, -120, timestamp_offset
        )

        await with_timeout(self.send_data(bits), 1500000, "ns")

        # Receive data
        actual = await with_timeout(self.get_data(), 150000, "ns")
        actual = unpack_complex(actual)

        # Reference data
        prn_data = prn.sample(
            1, 4.092e6, cycles * 4096, offset_samples=offset + timestamp_offset
        )
        mixed = quant * prn_data

        # Get correct offset
        mixed = mixed[len(mixed) - len(actual) - 1 : -1]

        result_corr = corr(mixed, actual)
        self.dut._log.info(
            f"IQ offset {offset}, timestamp offset {timestamp_offset}, corr={result_corr}, mixed samples={len(mixed)}"
        )

        # Graph data if failed
        if result_corr < 0.99:
            plt.figure()

            plt.subplot(2, 1, 1)
            plt.plot(mixed.real)
            plt.plot(mixed.imag)
            plt.xlim([0, 50])

            plt.subplot(2, 1, 2)
            plt.plot(actual.real)
            plt.plot(actual.imag)
            plt.xlim([0, 50])

            plt.tight_layout()
            plt.savefig("sim_build/comparison.png")

        assert result_corr > 0.99


@cocotb.test()
async def test_dut(dut):
    tb = TB(dut)

    await tb.reset()

    for phase_offset in [0, 10, 1234, 3456, 3910, 4091]:
        for iq_offset in [0, 5, 4050]:
            await tb.run_test(phase_offset, iq_offset)


from fpga_utils import test_runner

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level='RemovePrnWrapper',
        scala_name='RemovePrn',
        scala_object='RemovePrnVerilog',
        test_module='test_remove_prn',
        package='gps',
        proj_dir='../../..',
        source_dir='hw/spinal/gps',
        gen_dir='hw/gen',
    )
