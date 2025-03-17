#!/usr/bin/env python

import cocotb
from cocotbext.spi import SpiMaster, SpiBus, SpiConfig
from cocotb.triggers import Timer
import random

from fpga_utils import test_runner

# https://github.com/schang412/cocotbext-spi/tree/main

@cocotb.test()
async def test_spi_send_16bit(dut):

    spi_bus = SpiBus.from_prefix(dut, "io")  

    spi_config = SpiConfig(
        word_width    =   16,  
        sclk_freq     =   1e6,     # 1 MHz, T = 1 µs
        cpol          =   False,   # SPI Mode 1 : Master updates on rising edge, slave reads on falling edge
        cpha          =   True,   
        msb_first     =   True,
        cs_active_low =   True
    )

    spi_master = SpiMaster(spi_bus, spi_config)

    command = random.randint(0, 0xFFFF)
    await spi_master.write([command])  
    await Timer(4, units="us")  

    expected_rw_flag = (command >> 15) & 0x1  
    expected_addr = command & 0x7FFF  

    rw_flag = int(dut.io_rw.value)
    addr = int(dut.io_addr.value)
    received_flag = int(dut.io_received_flag.value)

    assert received_flag == 1, "Full command not received"
    assert rw_flag == expected_rw_flag, f"RW bit incorrect, expected {expected_rw_flag}, got {rw_flag}"
    assert addr == expected_addr, f"Address incorrect, expected {expected_addr:04x}, got {addr:04x}"

    print(f"Sent {command:04x}")
    print(f"RW {rw_flag}")
    print(f"Address {addr:04x}")

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="SpiSlave",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )