import cocotb
import numpy as np
import matplotlib.pyplot as plt
plt.switch_backend("Agg")

from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotbext.axi import AxiStreamSink, AxiStreamSource, AxiStreamBus, AxiStreamFrame

import sys
from pathlib import Path

# Hack to share fft_sim between multiple tests
fft_path = Path(__file__).resolve().parent.parent
sys.path.insert(len(sys.path), str(fft_path.resolve()))

from fft_sim import FFT_Sim, pack_complex, unpack_complex


@cocotb.test()
async def test_fft(dut):
    cocotb.start_soon(Clock(dut.aclk, 10, "ns").start())

    sim = FFT_Sim(dut, 12, 1)

    config_driver = AxiStreamSource(
        AxiStreamBus.from_prefix(dut, "s_axis_config"),
        dut.aclk,
        dut.aresetn,
        False,
    )

    data_driver = AxiStreamSource(
        AxiStreamBus.from_prefix(dut, "s_axis_data"),
        dut.aclk,
        dut.aresetn,
        False,
        byte_size=16,
    )

    data_receiver = AxiStreamSink(
        AxiStreamBus.from_prefix(dut, "m_axis_data"),
        dut.aclk,
        dut.aresetn,
        False,
        byte_size=16,
    )

    await config_driver.send([1]) # Forward FFT
    await config_driver.wait()

    in_data = 0.75 * np.exp(np.arange(4096)*2j*np.pi/10)

    packed_data = pack_complex(in_data)

    await data_driver.send(packed_data)
    await data_driver.wait()

    rx_frame = await data_receiver.recv()
    out_data = unpack_complex(rx_frame.tdata)
    out_data = out_data * 2**(int(rx_frame.tuser))

    ref_data = in_data
    ref_fft = np.fft.fft(ref_data)

    plt.figure(figsize=(6, 6))
    plt.subplot(3, 1, 1)
    plt.title("Reference FFT (Numpy)")
    plt.plot(ref_fft.real)
    plt.plot(ref_fft.imag)
    plt.subplot(3, 1, 2)
    plt.title("Xilinx FFT")
    plt.plot(out_data.real)
    plt.plot(out_data.imag)
    plt.subplot(3, 1, 3)
    plt.plot(np.abs(out_data - ref_fft))
    plt.tight_layout()
    plt.savefig("compare.png")
