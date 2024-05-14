import cocotb

from cocotb.clock import Clock 
from cocotb.triggers import ClockCycles

@cocotb.test()
async def test_three_wire_spi(dut):

    cocotb.start_soon(Clock(dut.clk, 10, "ns").start())
    dut.reset.value = 0
    await ClockCycles(dut.clk, 2)
    dut.reset.value = 1
    await ClockCycles(dut.clk, 2)
    dut.reset.value = 0
    await ClockCycles(dut.clk, 10000)
