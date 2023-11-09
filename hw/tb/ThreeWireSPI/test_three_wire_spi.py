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