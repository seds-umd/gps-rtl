import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, with_timeout

import numpy as np

from fpga_utils import test_runner
from fpga_utils.dsp import corr


async def send_values(dut, real, imag):
    for i in range(len(real)):
        dut.io_re.value = int(real[i])
        dut.io_im.value = int(imag[i])

        await RisingEdge(dut.clk)


@cocotb.test()
async def test_magnitude(dut, runs=1, num=8192):
    cocotb.start_soon(Clock(dut.clk, period=2, units="ns").start())

    for _ in range(runs):
        real = np.random.randint(0, 256, num, dtype=np.uint8)
        imag = np.random.randint(0, 256, num, dtype=np.uint8)

        dut.io_ready.value = 1

        await RisingEdge(dut.clk)

        cocotb.start_soon(send_values(dut, real, imag))

        real = real.astype(np.int8)
        imag = imag.astype(np.int8)

        # Prime pipeline
        await ClockCycles(dut.clk, 6)

        mag_ref = np.abs(real + 1j * imag)
        mag_res = []

        for i in range(num):
            mag_res.append(int(dut.io_mag.value))
            await RisingEdge(dut.clk)

        mag_res = np.array(mag_res)
        err = np.abs(mag_ref - mag_res)

        mag_corr = corr(mag_res, mag_ref)
        dut._log.info(
            f"Average err: {np.mean(err):0.2f}, max err: {np.max(err):0.2f}, corr: {mag_corr:0.3f}"
        )

        assert np.mean(err) < 4


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="Magnitude",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )
