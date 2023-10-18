import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, with_timeout


@cocotb.test()
async def test_fft(dut):
    print(dir(dut))
    cocotb.start_soon(Clock(dut.clk, period=2, units="ns").start())

    # dut.din.value = 0
    dut.phase.value = 4096 - 32

    for i in range(1000):
        await RisingEdge(dut.clk)

        # dut.phase.value = (dut.phase.value + 1) % 4096
