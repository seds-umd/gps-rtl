import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
import numpy as np
from fpga_utils import test_runner



@cocotb.test()
async def test_spi_counter(dut):


    




if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="SpiInterface",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )

