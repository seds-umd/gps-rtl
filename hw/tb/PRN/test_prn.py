import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles, with_timeout
from cocotbext import axi

import logging
import numpy as np
from gps import prn

@cocotb.test()
async def test_prn(dut):
    cocotb.start_soon(Clock(dut.clk, period=10, units="ns").start())

    axi_bus = axi.AxiStreamBus(dut)
    axi_bus._add_signal("tdata", "io_code_payload")
    axi_bus._add_signal("tvalid", "io_code_valid")
    axi_bus._add_signal("tready", "io_code_ready")
    axi_output = axi.AxiStreamSink(axi_bus, dut.clk, dut.reset, byte_size=1)
    axi_output.log.setLevel(logging.WARNING) # Get rid of log messages

    dut.reset.value = 1
    dut.io_sv.value = 0
    dut.io_set.value = 0

    await ClockCycles(dut.clk, 2)

    dut.reset.value = 0

    for divider in [1.0, 5/3, 2.9999, 4]:
        for sv in range(1, 33):
            dut.io_sv.value = sv-1
            dut.io_inc.value = int(2**16 / divider)
            dut.io_set.value = 1

            await RisingEdge(dut.clk)

            dut.io_set.value = 0

            code_recv = []
            code_len = int(np.ceil(1023*divider))
            code_ref = np.array(prn.sample(sv, 1.023e6*divider, code_len).real, dtype=int)

            for _ in range(code_len):
                frame = await with_timeout(axi_output.recv(), 100, "ns")
                code_recv.append(frame.tdata[0])
            
            code_recv = np.array(code_recv)
            code_recv[code_recv == 0] = -1

            # corr = np.correlate(code_ref, code_recv)
            # assert np.max(corr) > code_len * 0.99, f"{np.max(corr)/code_len}, {divider}, {sv}"

            assert len(code_ref) == len(code_recv), f"{len(code_ref)}, {len(code_recv)}"
            matched = code_ref == code_recv
            wrong = int(np.argmin(matched))
            assert matched.all(), f"{sv}, {divider}, {wrong}, {code_ref[wrong-3:wrong+3]}, {code_recv[wrong-3:wrong+3]}"
