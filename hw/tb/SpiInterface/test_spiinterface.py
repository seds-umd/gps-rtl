import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
import numpy as np
from fpga_utils import test_runner


@cocotb.test()
async def minimal_clock_test(dut):
    cocotb.start_soon(Clock(dut.io_sclk, 20, units="ns").start())  # This should just work
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    dut.io_reset.value = 0
    dut.io_cs.value = 1
    dut.io_sclk.value = 0
    dut.io_mosi.value = 0

    dut._log.info("Asserting reset")
    dut.io_reset.value = 1
    await Timer(50, units="ns")

    dut._log.info("Deasserting reset - counter should reset to 0")
    dut.io_reset.value = 0
    await Timer(50, units="ns")


    for count in range(50):
        dut.io_cs.value = 0
        await RisingEdge(dut.io_sclk)
        for _ in range(16):
            await RisingEdge(dut.io_sclk)
            dut.io_mosi.value = np.random.randint(0, 2)
        dut.io_cs.value = 1
        await Timer(10*16, units="ns")


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="SpiInterface",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )
