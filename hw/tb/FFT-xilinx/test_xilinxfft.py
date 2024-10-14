#!/usr/bin/env python

import cocotb
from cocotb.clock import Clock
from cocotbext.axi import AxiStreamSink, AxiStreamSource, AxiStreamBus, AxiStreamFrame

import numpy as np
import matplotlib.pyplot as plt

plt.switch_backend("Agg")

import fpga_utils
from fpga_utils import test_runner
from fpga_utils.fft_sim import FFT_Sim, fft_pack_complex, fft_unpack_complex


@cocotb.test()
async def test_fft(dut):
    cocotb.start_soon(Clock(dut.aclk, 10, "ns").start())
    dut._log.info("test")

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

    await config_driver.send([1])  # Forward FFT
    await config_driver.wait()

    in_data = 0.75 * np.exp(np.arange(4096) * 2j * np.pi / 10)

    packed_data = fft_pack_complex(in_data)

    await data_driver.send(packed_data)
    await data_driver.wait()

    rx_frame = await data_receiver.recv()
    out_data = fft_unpack_complex(rx_frame.tdata)
    out_data = out_data * 2 ** (int(rx_frame.tuser))

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

if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="XilinxFFT",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
        verilog_sources=["hw/verilog/XilinxFFT.v"],
        scala=False,
    )
