#!/usr/bin/env python

import cocotb
from cocotb.clock import Clock 
from cocotb.triggers import RisingEdge, Timer

from fpga_utils import test_runner

@cocotb.test()
async def test_counter(dut):
    cocotb.start_soon(Clock(dut.clk, period = 10, units = 'ns').start())

    # Drives reset high and then releases, ensuring FSM starts in idle
    dut.reset.value = 1
    await Timer(30, units = 'ns')
    dut.reset.value = 0
    await RisingEdge(dut.clk)

    # Asserts that FSM starts in idle
    expected = 0
    assert int(dut.io_counter.value) == expected, "FSM is not in idle when it should be"

    # Tests FSM -> runs clock until max count is reached and asserts along the way
    breakFlag = False
    while(not breakFlag):
        expected += 1
        await RisingEdge(dut.clk)

        assert int(dut.io_counter.value) == expected, "Counter holds incorrect value"

        if(expected >= 15):
            assert dut.io_done.value, "Counter is still running when it should be stopped"
            breakFlag = True
        else:
            assert not dut.io_done.value, "Counter is not running when it should be"

    return


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="VedantMiniProject",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir=".",
    )