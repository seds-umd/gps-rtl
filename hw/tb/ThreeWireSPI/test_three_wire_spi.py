import cocotb

from cocotb.clock import Clock 
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_three_wire_spi(dut):

    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())
    dut.rst.value = 0
    await ClockCycles(dut.clk, 1000)
    dut.rst.value = 1
    await ClockCycles(dut.clk, 2)
    dut.rst.value = 0
    await ClockCycles(dut.clk, 10000)

from fpga_utils import test_runner

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level='ThreeWireSpi',
        scala=False,
        verilog_sources=['hw/verilog/three_wire_spi.v'],
        test_module='test_three_wire_spi',
        package='gps',
        proj_dir='../../..',
        source_dir='hw/spinal/gps',
        gen_dir='hw/gen',
    )
