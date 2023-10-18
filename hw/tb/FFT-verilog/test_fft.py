import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, with_timeout


@cocotb.test()
async def test_fft(dut):
    cocotb.start_soon(Clock(dut.clk, period=2, units="ns").start())

    dut.din_re.value = 0
    dut.din_im.value = 0
    dut.phase.value = 4096 - 32

    for i in range(12600):
        await RisingEdge(dut.clk)

        dut.phase.value = (dut.phase.value + 1) % 4096
