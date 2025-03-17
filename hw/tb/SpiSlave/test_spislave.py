#!/usr/bin/env python

import cocotb
from cocotbext.spi import SpiMaster, SpiBus, SpiConfig
from cocotb.triggers import Timer

from fpga_utils import test_runner

# https://github.com/schang412/cocotbext-spi/tree/main

@cocotb.test()
async def test_spi_send_1bit(dut):

    spi_bus = SpiBus.from_prefix(dut, "io")  

    spi_config = SpiConfig(
        word_width    =   1,  
        sclk_freq     =   1e6,     # 1 MHz, T = 1 µs
        cpol          =   False,   # Mode 1 : Master updates on rising edge, slave reads on falling edge
        cpha          =   True,   
        msb_first     =   True,
        cs_active_low =   True
    )

    spi_master = SpiMaster(spi_bus, spi_config)

    command = [1]  
    await spi_master.write(command)
    await Timer(1, units="us") 

    received_bit = int(dut.io_received_bit.value)

    assert received_bit == 1, f"Received {received_bit}"
    
    print(f"Successfully received {received_bit}")

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="SpiSlave",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )