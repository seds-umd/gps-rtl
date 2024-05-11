import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotbext import axi

import numpy as np
import logging


# Calculate correlation between two signals, between 1 and -1
def corr(a: np.ndarray, b: np.ndarray):
    assert len(a) == len(b), f"Arrays must be the same length, {len(a)} != {len(b)}"

    a_norm = (a - np.mean(a)) / np.std(a)
    b_norm = (b - np.mean(b)) / np.std(b)

    return np.abs(np.sum(a_norm * b_norm.conjugate())) / len(a)


# Random pause generator for AXI bus
def random_pause():
    while True:
        yield np.random.choice([0, 1])


def stream_axis_bus(dut, prefix: str, fragment: bool = False):
    axi_bus = axi.AxiStreamBus(dut)

    if fragment:
        axi_bus._add_signal("tdata", prefix + "payload_fragment")
        axi_bus._add_signal("tlast", prefix + "payload_last")
    else:
        axi_bus._add_signal("tdata", prefix + "payload")

    axi_bus._add_signal("tvalid", prefix + "valid")
    axi_bus._add_signal("tready", prefix + "ready")

    return axi_bus


def axis_sink(dut, prefix: str, fragment: bool = False, **kwargs):
    bus = stream_axis_bus(dut, prefix, fragment)
    sink = axi.AxiStreamSink(bus, dut.clk, dut.reset, **kwargs)
    sink.log.setLevel(logging.WARNING)

    return sink


def axis_source(dut, prefix: str, fragment: bool = False, **kwargs):
    bus = stream_axis_bus(dut, prefix, fragment)
    source = axi.AxiStreamSource(bus, dut.clk, dut.reset, **kwargs)
    source.log.setLevel(logging.WARNING)

    return source


class TB_Template:
    def __init__(self, dut, period=10):
        self.dut = dut

        cocotb.start_soon(Clock(self.dut.clk, period=period, units="ns").start())

    async def reset(self, delay=2):
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, delay)
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, delay)
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, delay)
