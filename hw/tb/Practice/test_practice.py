
'''
#!/usr/bin/env python

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer

from fpga_utils import test_runner

@cocotb.test()
async def test_counter(dut):

    clock = Clock(dut.clk, 10, units="ns") # 100 MHz
    cocotb.start_soon(clock.start())

    dut.reset.value = 1  
    await Timer(5, units="ns")  
    dut.reset.value = 0 

    for cycle in range(20):
        await RisingEdge(dut.clk)
        actual = int(dut.io_output.value)
        cocotb.log.info(f"Cycle {cycle}: output = {actual}")
        assert actual == cycle % 16, f"Expected {cycle % 16}, got {actual}"






if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="Practice",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )

    
'''


#!/usr/bin/env python

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge
from cocotb.triggers import Timer

from fpga_utils import test_runner




@cocotb.test()
async def test_name(dut): #dut = 'device under test'
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())

    dut.reset.value = 1

    await Timer(5, units="ns")

    dut.reset.value = 0




    for i in range(0,20):
        await RisingEdge(dut.clk)
        output = dut.io_output.value
        cocotb.log.info(int(output))

        if i <= 15:
            if i == output:
                print(output)
            else: 
                print("u fucked up bro im negl")

        if i > 15:
            cycle = i - 15
            if cycle%16 == output:
                print(output)
            else:  
                print("u fucked up again twin no bap")
        i+=1


        















if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="Practice",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )