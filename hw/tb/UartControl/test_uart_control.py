import cocotb
import cocotb.result
from cocotb.triggers import ClockCycles
from cocotbext import uart

import numpy as np
import sys
import logging
from pathlib import Path

from fpga_utils import TbTemplate, axis_source, axis_sink, ratio_pause, complex_to_2bit


class TB(TbTemplate):
    def __init__(self, dut, baud=115200):
        super().__init__(dut, period=20)

        self.iq_in = axis_source(dut, "io_iq_", byte_size=4)
        self.iq_in.set_pause_generator(ratio_pause())
        self.uart_source = uart.UartSource(dut.io_uart_rxd, baud)
        self.uart_sink = uart.UartSink(dut.io_uart_txd, baud)

        self.uart_source.log.setLevel(logging.WARNING)
        self.uart_sink.log.setLevel(logging.WARNING)

        self.spi_data = axis_sink(dut, "io_spi_data_", byte_size=32)

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

    commanded_len = 5

    await tb.send_uart([commanded_len])
    await tb.uart_source.wait()

    data = complex_to_2bit(data)
    await tb.send_iq(data)

    data = np.array(data)
    # First data goes in lower bits
    expected = data[::2] | (data[1::2] << 4)
    expected = expected.astype(np.uint8).tobytes()

    CLK_PER_BYTE = int(10 * CLK / BAUD)
    await ClockCycles(dut.clk, CLK_PER_BYTE * 2**commanded_len)

    actual = await tb.get_uart()

    # Account for data dropped due to FIFO overflow
    assert actual in expected

    assert len(actual) == 2**commanded_len

    # Try register write
    for _ in range(10):
        word = np.random.randint(0, 2**32 - 1)
        await tb.send_uart([0x20])
        await tb.send_uart(int(word).to_bytes(4, 'big'))

        actual = (await tb.spi_data.read(1))[0]
        assert word == actual


from fpga_utils import test_runner

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level='UartControlWrapper',
        scala_name='UartControl',
        scala_object='UartControlVerilog',
        test_module='test_uart_control',
        package='gps',
        proj_dir='../../..',
        source_dir='hw/spinal/gps',
        gen_dir='hw/gen',
    )
