import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge

from fpga_utils import test_runner


@cocotb.test()
async def test(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    maxcycles = 20
    j = 0
    
    dut.reset.value = 1
    await RisingEdge(dut.clk)
    dut.reset.value = 0

    for i in range(maxcycles):
        await RisingEdge(dut.clk)
        #avoids errors when 0 is repeated multiple times
        if int(dut.io_counterOut.value) != 0:
            j+=1
            assert(int(dut.io_counterOut.value)==j)
        #print statements for testing purposes
        #print(int(dut.io_counterOut.value))
        #print(j)
        if int(dut.io_counterOut.value) == 15:
            break
    #asserting whether the counter entered DONE state
    await RisingEdge(dut.clk)
    assert int(dut.io_result.value) == 1

#pointing the test to hw/gen so it finds the Counter.v file
if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="Counter",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen"
    )