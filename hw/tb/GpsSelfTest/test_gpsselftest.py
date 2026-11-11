"""Board self-test design end to end: UART commands in, acquisition result lines out.

Uses the same protocol and checking code as the host tool (scripts/arty_selftest.py)
and the same emulator model, so a pass here means the host tool's expectations
hold for this RTL.

The FFT is the Xilinx bit-accurate C model, as in the other acquisition benches.
Set FFT_MODEL=numpy to substitute a floating-point stand-in with block scaling:
useful for working on the UART and control logic where the C model is not
available, but not evidence about FFT arithmetic.
"""
import logging
import os
from pathlib import Path
import sys
import types

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, FallingEdge, with_timeout
from cocotbext import uart
import numpy as np

from fpga_utils import test_runner

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
import arty_selftest as host  # noqa: E402
import max_emulator as model  # noqa: E402

BAUD = 1250000  # GpsSelfTestSim: divides the 50 MHz clock exactly
CHANNELS = 2
SIM_COARSE_BINS = 2


def install_numpy_fft():
    """Stand in for gps.xilinx_fft with numpy and power-of-two block scaling."""

    class Outputs:
        blk_exp = 0

    class Fft:
        def __init__(self, size=6, arch=2, input_width=8, twiddle_width=10):
            self.outputs = Outputs()
            self.limit = (2 ** (input_width - 1) - 1) / 2 ** (input_width - 1)
            self.scale = 2 ** (input_width - 1)

        def run(self, x, inv=False):
            spectrum = np.fft.ifft(x) * len(x) if inv else np.fft.fft(x)
            exponent = 0
            while max(np.abs(spectrum.real).max(), np.abs(spectrum.imag).max()) / 2**exponent > self.limit:
                exponent += 1
            self.outputs.blk_exp = exponent
            scaled = spectrum / 2**exponent
            return np.round(scaled.real * self.scale) / self.scale + 1j * np.round(scaled.imag * self.scale) / self.scale

    module = types.ModuleType("gps.xilinx_fft")
    module.Fft = Fft
    sys.modules["gps.xilinx_fft"] = module


class TB:
    def __init__(self, dut):
        self.dut = dut
        self.source = uart.UartSource(dut.io_uart_rxd, BAUD)
        self.sink = uart.UartSink(dut.io_uart_txd, BAUD)
        self.source.log.setLevel(logging.WARNING)
        self.sink.log.setLevel(logging.WARNING)
        self.buffer = b""
        self.results = []

    async def start(self):
        dut = self.dut
        dut.reset.value = 1
        cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())
        cocotb.start_soon(Clock(dut.io_clk_ser, 61, units="ns").start())

        if os.environ.get("FFT_MODEL", "").lower() == "numpy":
            dut._log.warning("FFT_MODEL=numpy: floating-point FFT stand-in, not the Xilinx C model")
            install_numpy_fft()
        from fpga_utils.fft_sim import FFT_Sim

        self.fft = FFT_Sim(dut.core_gps.acq.fft_inst, 12, 1, store=False)
        self.fft.log.setLevel(logging.WARNING)

        await ClockCycles(dut.io_clk_ser, 8)
        await FallingEdge(dut.clk)
        dut.reset.value = 0

    async def line(self):
        """Next complete line from the board."""
        while b"\n" not in self.buffer:
            self.buffer += bytes(await self.sink.read())
        raw, self.buffer = self.buffer.split(b"\n", 1)
        assert raw.endswith(b"\r"), f"line must end with CR LF: {raw!r}"
        return raw

    async def next(self):
        while True:
            parsed = host.parse_line(await self.line())
            if parsed is not None:
                return parsed

    async def command(self, data, kind):
        await self.source.write(data)
        while True:
            parsed = await with_timeout(self.next(), 1, "ms")
            if isinstance(parsed, host.Result):
                self.results.append(parsed)
            elif parsed.kind == kind or parsed.kind == "e":
                return parsed

    async def write(self, address, value):
        reply = await self.command(host.write_command(address, value), "w")
        assert reply.kind == "w" and reply.address == address, reply
        return reply.value

    async def read(self, address):
        reply = await self.command(host.read_command(address), "q")
        assert reply.kind == "q" and reply.address == address, reply
        return reply.value

    async def run_scenario(self, scenario, count):
        """Stop, program, start and return the first count results."""
        assert await self.write(host.REG_CTRL, 0) == 0
        self.results.clear()
        for address, value in host.scenario_writes(scenario, CHANNELS):
            assert await self.write(address, value) == value, f"register {address:#04x} did not read back"
        assert await self.write(host.REG_CTRL, 1) == 1
        while len(self.results) < count:
            parsed = await with_timeout(self.next(), 16, "ms")
            assert isinstance(parsed, host.Result), parsed
            self.results.append(parsed)
        results, self.results = self.results[:count], self.results[count:]
        return results


@cocotb.test(timeout_time=20, timeout_unit="ms")
async def registers_and_protocol(dut):
    """Identify, write, read back, read-only registers and error replies."""
    tb = TB(dut)
    await tb.start()

    # Stop the default run first so no result lines interleave.
    assert await tb.write(host.REG_CTRL, 0) == 0
    assert int(dut.io_leds.value) & 0b0010 == 0, "running LED must be off while stopped"

    reply = await tb.command(host.identify_command(), "i")
    assert (reply.kind, reply.address, reply.value) == ("i", host.REG_ID, host.ID_WORD)
    assert await tb.read(host.REG_ID) == host.ID_WORD
    assert await tb.read(host.REG_INFO) == CHANNELS | (SIM_COARSE_BINS << 8)

    # Power-on defaults: satellite 7 on channel 0, channel 1 off.
    assert await tb.read(host.REG_CHANNEL_BASE) == 7 | (1 << 8) | (96 << 16)
    assert await tb.read(host.REG_CHANNEL_BASE + 1) == 16 << 17
    assert await tb.read(host.REG_CHANNEL_BASE + 2) == 1000
    assert await tb.read(host.REG_CHANNEL_BASE + host.REG_CHANNEL_STRIDE) & 0x100 == 0
    assert await tb.read(host.REG_QUANT) == 64 << 8

    # Every writable register keeps what it is given, within its width.
    for address, value, expected in [
        (host.REG_QUANT, 0xFFFFA55A, 0xA55A),
        (host.REG_SEED, 0xDEADBEEF, 0xDEADBEEF),
        (host.REG_CHANNEL_BASE, 0xFFFFFFFF, 0x00FF013F),
        (host.REG_CHANNEL_BASE + 1, 0x89ABCDEF, 0x89ABCDEF),
        (host.REG_CHANNEL_BASE + 2, 0xFFFFFABC, 0xABC),
        (host.REG_CHANNEL_BASE + host.REG_CHANNEL_STRIDE + 1, 0x01234567, 0x01234567),
    ]:
        assert await tb.write(address, value) == expected, f"register {address:#04x}"
        assert await tb.read(address) == expected

    # Read-only and unmapped registers ignore writes.
    assert await tb.write(host.REG_ID, 0) == host.ID_WORD
    assert await tb.write(0x7F, 0x12345678) == 0

    # Lower case, embedded spaces and CR LF line endings are accepted.
    await tb.source.write(b"w 04 0000 00aa\r\n")
    reply = await with_timeout(tb.next(), 1, "ms")
    assert (reply.kind, reply.address, reply.value) == ("w", host.REG_SEED, 0xAA)

    # Bad command letters and bad hex digits get an error reply, then the parser recovers.
    # A line end before a command is complete cancels it the same way.
    for bad in (b"X", b"W0G", b"W04 1234\n", b"Q\r"):
        await tb.source.write(bad)
        reply = await with_timeout(tb.next(), 1, "ms")
        assert reply.kind == "e", (bad, reply)
    assert await tb.read(host.REG_SEED) == 0xAA

    # Two commands sent back to back, the second arriving while the first
    # reply is still on the wire: both replies must come out, in order.
    await tb.source.write(host.read_command(host.REG_ID) + host.read_command(host.REG_SEED))
    first = await with_timeout(tb.next(), 1, "ms")
    second = await with_timeout(tb.next(), 1, "ms")
    assert (first.address, first.value) == (host.REG_ID, host.ID_WORD)
    assert (second.address, second.value) == (host.REG_SEED, 0xAA)
    assert tb.results == [], "no results may appear while stopped"

    # While running, emulator registers are locked: the write is refused and nothing changes.
    assert await tb.write(host.REG_CTRL, 1) == 1
    for address in (host.REG_QUANT, host.REG_SEED, host.REG_CHANNEL_BASE + 1,
                    host.REG_CHANNEL_BASE + host.REG_CHANNEL_STRIDE + 2):
        reply = await tb.command(host.write_command(address, 0x55555555), "w")
        assert reply.kind == "e", f"write to {address:#04x} while running must be refused"
    assert await tb.read(host.REG_SEED) == 0xAA
    assert await tb.write(host.REG_CTRL, 0) == 0
    assert await tb.write(host.REG_SEED, 0x77) == 0x77


@cocotb.test(timeout_time=60, timeout_unit="ms")
async def acquires_programmed_satellites(dut):
    """Two runs with different signals; results match what the emulator was told to send."""
    tb = TB(dut)
    await tb.start()

    # Run 1: the fixture the GpsTop bench uses (satellite 2, fine bin 8, phase 37).
    scenario = host.Scenario("sim: SV 2", [model.Channel(2, 37, host.fine(8))])
    results = await tb.run_scenario(scenario, 2)
    dut._log.info(f"Run 1: {results}")
    assert host.check_order(results) == []
    assert host.check_results(scenario, results) == []
    assert results[1].metric > 8 and results[1].metric > 4 * results[0].metric

    # Registers stay readable while results are streaming, and the lines do not interleave.
    for _ in range(3):
        assert await tb.read(host.REG_ID) == host.ID_WORD
    status = await tb.read(host.REG_STATUS)
    assert status & 1 == 0, "sample overflow"
    assert status >> 8 >= 2, "result counter must count delivered results"
    assert int(dut.io_leds.value) & 0b1010 == 0b0010, "running LED on, overflow LED off"

    # Run 2: a different satellite, negative Doppler, late code phase, second
    # channel carrying a satellite the sweep will not reach. Satellite 1 comes
    # first again, so the stop/start cycle must have reset the core.
    scenario = host.Scenario(
        "sim: SV 1 with SV 20 in the background",
        [model.Channel(1, 4000, host.fine(-11), 80), model.Channel(20, 123, host.fine(5), 40)],
    )
    results = await tb.run_scenario(scenario, 1)
    dut._log.info(f"Run 2: {results}")
    assert results[0].sv == 1
    assert host.check_results(scenario, results) == [f"satellite 20: no result received"]
    status = await tb.read(host.REG_STATUS)
    assert status & 1 == 0, "sample overflow"


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="GpsSelfTestSim", scala_name="GpsSelfTest", scala_object="GpsSelfTestSimVerilog",
        test_module="test_gpsselftest", package="gps", proj_dir="../../..",
        source_dir="hw/spinal/gps", gen_dir="hw/gen",
        spinal_sources=["MaxEmulator", "GpsTop", "AcquisitionModular", "MaxInterface", "PrnGenerator"],
        verilog_sources=["hw/verilog/XilinxFFT.v"],
    )
