import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles, with_timeout
from cocotbext import axi

import numpy as np
import sys
from pathlib import Path

from fpga_utils.fft_sim import fft_pack_complex as pack_complex, fft_unpack_complex as unpack_complex
from fpga_utils import TbTemplate, axis_sink, axis_source, corr, random_pause


class TB(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        self.input = axis_source(dut, "io_input_", fragment=True, byte_size=16)
        self.output = axis_sink(dut, "io_mag_", fragment=True)
        self.output.set_pause_generator(random_pause())

    async def send_data(self, data: bytes):
        await with_timeout(self.input.send(data), 1000000, "ns")
        await with_timeout(self.input.wait(), 1000000, "ns")

    async def get_data(self):
        frame: axi.AxiStreamFrame = await with_timeout(
            self.output.recv(), 1000000, "ns"
        )

        return frame.tdata


@cocotb.test()
async def test_magnitude_stream(dut):
    tb = TB(dut)

    await tb.reset()

    N = 1024
    runs = 8

    for _ in range(runs):
        data = np.random.uniform(-1, 1, N) + 1j * np.random.uniform(-1, 1, N)

        await tb.send_data(pack_complex(data))

        expected = np.abs(data)
        actual = await tb.get_data()
        mag_corr = corr(expected, actual)

        tb.dut._log.info(f"Correlation: {mag_corr:0.3f}")
        assert len(actual) == N
        assert mag_corr > 0.99, f"Magnitude correlation too low: {mag_corr}"


from fpga_utils import test_runner

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level='MagnitudeStreamWrapper',
        scala_name='Magnitude',
        scala_object='MagnitudeStreamVerilog',
        test_module='test_magnitude_stream',
        package='gps',
        proj_dir='../../..',
        source_dir='hw/spinal/gps',
        gen_dir='hw/gen',
    )
