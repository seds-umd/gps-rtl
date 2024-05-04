import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotbext import axi

import numpy as np
import logging

import sys
from pathlib import Path

# Hack to share fft_sim between multiple tests
fft_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(fft_path.resolve()))

from fft_sim import pack_complex, unpack_complex
from utils import corr, random_pause


class TB:
    def __init__(self, dut, period=10) -> None:
        self.dut = dut

        # Clock
        cocotb.start_soon(Clock(self.dut.clk, period, "ns").start())

        # Input bus
        in_bus = axi.AxiStreamBus(self.dut)
        in_bus._add_signal("tdata", "io_iq_in_payload")
        in_bus._add_signal("tready", "io_iq_in_ready")
        in_bus._add_signal("tvalid", "io_iq_in_valid")
        self.in_bus = axi.AxiStreamSource(in_bus, dut.clk, byte_size=16)
        self.in_bus.log.setLevel(logging.WARNING)

        # Output bus
        out_bus = axi.AxiStreamBus(self.dut)
        out_bus._add_signal("tdata", "io_iq_out_payload")
        out_bus._add_signal("tready", "io_iq_out_ready")
        out_bus._add_signal("tvalid", "io_iq_out_valid")
        self.out_bus = axi.AxiStreamSink(out_bus, dut.clk, byte_size=16)
        self.out_bus.log.setLevel(logging.WARNING)

        # Random timing
        self.in_bus.set_pause_generator(random_pause())
        self.out_bus.set_pause_generator(random_pause())

    # Samples must be normalized to +-1
    async def run(self, samples: np.ndarray):
        samples = pack_complex(samples)

        await self.in_bus.send(samples)
        await self.in_bus.wait()
        await ClockCycles(self.dut.clk, 10)

        data = await self.out_bus.read(len(samples) // 8)

        return unpack_complex(data)

    async def reset(self):
        self.dut.reset.value = 0
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 1
        await ClockCycles(self.dut.clk, 2)
        self.dut.reset.value = 0


@cocotb.test()
async def test_decimate(dut):
    tb = TB(dut)

    await tb.reset()

    for N in [16, 64, 256, 1024, 4096]:
        ref = np.random.randn(N) + 1j * np.random.randn(N)
        ref /= np.max(np.abs(ref))
        ref_dec = np.sum(ref.reshape(-1, 8), axis=1) / 8

        result = await tb.run(ref)
        dec_corr = corr(ref_dec, result)

        dut._log.info(f"N={N}, correlation={dec_corr:0.5f}")
        assert dec_corr > 0.99
