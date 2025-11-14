import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from cocotb.clock import Clock
import numpy as np
from fpga_utils import test_runner


@cocotb.test()
async def bram_memory_test(dut):
    # Start both clocks
    bits = [0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    cocotb.start_soon(Clock(dut.clk, 4, units="ns").start())
    dut.io_reset.value = 0   # optional, not used internally

    await Timer(100, units="ns")   # hold reset high briefly
     

    dut.io_w_address = 1
    dut.io_w_data = 55
    dut.io_w_enable = 1

    await Timer(100, units="ns")   # hold reset high briefly

    dut.io_r_address = 1
    read_data = dut.io_r_data

    await Timer(100, units="ns")   # hold reset high briefly

    


    """"
    # Assert reset for a few cycles
    dut.reset.value = 1
    dut.io_reset.value = 0   # optional, not used internally
    dut.io_cs.value = 1
    dut.io_sclk.value = 0
    dut.io_mosi.value = 0

    dut._log.info("Asserting reset...")
    await Timer(100, units="ns")   # hold reset high briefly

    # Deassert reset so FSM can start
    dut.reset.value = 0
    dut._log.info("Deasserting reset")

    # Give FSM time to initialize
    await Timer(100, units="ns")

    #test write
    dut.io_cs.value = 0
    await RisingEdge(dut.io_sclk)
    dut.io_miso.value = 0

    for b in range(15): 
        await RisingEdge(dut.io_sclk)
        dut.io_mosi.value = bits[b]    
    for _ in range(16):
        await RisingEdge(dut.io_sclk)
        dut.io_mosi.value = np.random.randint(0, 2)
    dut.io_cs.value=1

    await RisingEdge(dut.io_sclk)
    await RisingEdge(dut.io_sclk)
    await RisingEdge(dut.io_sclk)

    dut.io_cs.value = 0
    await RisingEdge(dut.io_sclk)
    dut.io_miso.value = 1

    for i in range(15):
        await RisingEdge(dut.io_sclk)
        dut.io_mosi.value = bits[i]
    
    for l in range(24):
        await RisingEdge(dut.io_sclk)
"""
        

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="BramTest",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )

