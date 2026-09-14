"""Check the words actually clocked out to the MAX2769, including backpressure."""
import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import ClockCycles, FallingEdge, ReadOnly, RisingEdge, with_timeout

STARTUP_WORDS = [
    0xA2951A30, 0x85504881, 0xEAFE1DC2, 0x9EC00083, 0x0C000804,
    0x80000705, 0x80000006, 0x400400B7, 0xE6FFBF22, 0xE6FFDF22,
]

async def receive_spi(dut, words):
    previous_cs, previous_clock = 1, 0
    word, bits = 0, 0
    initialized = False
    while True:
        await RisingEdge(dut.clk)
        await ReadOnly()
        if dut.reset.value:
            previous_cs, previous_clock = 1, 0
            word, bits = 0, 0
            continue
        if not dut.io_spi_cs.value.is_resolvable:
            assert not initialized, "Chip select became unknown after initialization"
            continue
        initialized = True
        cs, clock = int(dut.io_spi_cs.value), int(dut.io_spi_sclk.value)
        if not cs and previous_cs:
            word, bits = 0, 0
        if not cs and clock and not previous_clock:
            word = (word << 1) | int(dut.io_spi_sdata.value)
            bits += 1
        if cs and not previous_cs:
            assert bits == 32, f"Expected 32 SPI clock edges, got {bits}"
            words.put_nowait(word)
        previous_cs, previous_clock = cs, clock

async def send_words(dut, values):
    for word in values:
        await FallingEdge(dut.clk)
        dut.io_data_payload.value = word
        dut.io_data_valid.value = 1
        while True:
            await RisingEdge(dut.clk)
            if dut.io_data_ready.value:
                break
    await FallingEdge(dut.clk)
    dut.io_data_valid.value = 0

@cocotb.test(timeout_time=500, timeout_unit="us")
async def test_startup_and_consecutive_writes(dut):
    dut.reset.value = 1
    dut.io_data_valid.value = 0
    dut.io_data_payload.value = 0
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await ClockCycles(dut.clk, 4)
    received = Queue()
    cocotb.start_soon(receive_spi(dut, received))
    await FallingEdge(dut.clk)
    dut.reset.value = 0
    # Queue writes during startup: ready must hold them until configuration ends.
    writes = [0x12345678, 0x8000000F, 0x00000000, 0xFFFFFFFF, 0xA5A55A5A]
    sender = cocotb.start_soon(send_words(dut, writes))
    for index, expected in enumerate(STARTUP_WORDS + writes):
        actual = await with_timeout(received.get(), 20, "us")
        assert actual == expected, f"SPI word {index}: {actual:#010x} != {expected:#010x}"
    await sender
    await ClockCycles(dut.clk, 1000)
    assert received.empty(), "Unexpected duplicate SPI word"


from fpga_utils import test_runner

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level='MaxSpiConfig',
        test_module='test_max_spi_config',
        package='gps',
        proj_dir='../../..',
        source_dir='hw/spinal/gps',
        gen_dir='hw/gen',
    )
