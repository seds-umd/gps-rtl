import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles
from cocotbext import uart

import numpy as np
import sys
import logging
from pathlib import Path

utils_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(utils_path.resolve()))

from utils import TB_Template, axis_source, iq_pause, pack_iq


class TB(TB_Template):
    def __init__(self, dut, baud=115200):
        super().__init__(dut, period=20)

        self.iq_in = axis_source(dut, "io_iq_", byte_size=4)
        self.iq_in.set_pause_generator(iq_pause())
        self.uart_source = uart.UartSource(dut.io_uart_rxd, baud)
        self.uart_sink = uart.UartSink(dut.io_uart_txd, baud)

        self.uart_source.log.setLevel(logging.WARNING)
        self.uart_sink.log.setLevel(logging.WARNING)

    async def send_iq(self, data):
        await self.iq_in.send(data)

    async def send_uart(self, data: bytes):
        await self.uart_source.write(data)

    async def get_uart(self):
        return await self.uart_sink.read()


@cocotb.test()
async def test_dut(dut):
    BAUD = 1000000  # Hz
    CLK = 50e6  # Hz
    tb = TB(dut, baud=BAUD)

    await tb.reset()

    N = 256

    data = np.random.uniform(-1, 1, N) + 1j * np.random.uniform(-1, 1, N)

    await tb.send_uart(b"0")
    await tb.uart_source.wait()

    data = pack_iq(data)
    await tb.send_iq(data)

    data = np.array(data)
    # First data goes in lower bits
    expected = data[::2] | (data[1::2] << 4)
    expected = expected.astype(np.uint8).tobytes()

    CLK_PER_BYTE = int(10 * CLK / BAUD)
    await ClockCycles(dut.clk, CLK_PER_BYTE * len(expected))

    actual = await tb.get_uart()

    # Account for data dropped due to FIFO overflow
    assert actual in expected
