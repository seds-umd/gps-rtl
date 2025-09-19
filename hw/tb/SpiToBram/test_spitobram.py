#!/usr/bin/env python

import cocotb
from cocotb.clock import Clock
from cocotbext.spi import SpiMaster, SpiBus, SpiConfig
from cocotb.triggers import Timer
import random

from fpga_utils import test_runner

# https://github.com/schang412/cocotbext-spi/tree/main

@cocotb.test()
async def test_spi_read_transaction(dut):

    cocotb.start_soon(Clock(dut.clk, 50, units="ns").start())   # 20 MHz, T = 50 ns

    dut.reset.value = 1
    await Timer(200, units="ns")
    dut.reset.value = 0
    await Timer(200, units="ns")

    spi_bus = SpiBus.from_prefix(dut, "io")  

    spi_config = SpiConfig(
        word_width=8,
        sclk_freq=1e5,    # 100 kHz, T = 10 μs
        cpol=False,
        cpha=True,
        msb_first=True,
        cs_active_low=True
    )

    spi_master = SpiMaster(spi_bus, spi_config)

    dut.io_bram_rddata.value = 0xABCD

    cmd = 0x8010         # 1000 0000 0001 0000 -> RW=1, address=0x0010
    await spi_master.write([cmd >> 8, cmd & 0xFF])  

    await spi_master.write([0x00])  

    response = await spi_master.read(2) 
    read_value = (response[0] << 8) | response[1]

    assert read_value == 0xABCD, f"Expected 0xABCD, got 0x{read_value:04X}"
    print(f"Received: 0x{read_value:04X}")

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="SpiToBram",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )