#!/usr/bin/env python

import cocotb
from cocotb.clock import Clock
from cocotb.queue import Queue
from cocotb.triggers import ClockCycles, Timer, with_timeout
from cocotbext.eth import GmiiFrame, GmiiPhy
import fpga_utils
from fpga_utils import test_runner
from fpga_utils.fft_sim import FFT_Sim

import logging
import numpy as np
from pathlib import Path
from scapy.layers.l2 import Ether, ARP
from scapy.layers.inet import IP, UDP


class TB:
    def __init__(self, dut, host_mac, device_mac, host_ip, device_ip):
        self.dut = dut

        # MAX2769 interface, just sending zeros for now, running faster to speed up sim
        # cocotb.start_soon(Clock(self.dut.io_max_clk_ser, 10, "ns").start())
        cocotb.start_soon(Clock(self.dut.io_max_clk_ser, 1000 / 16, "ns").start())
        self.dut.io_max_data_in.value = 0
        self.dut.io_max_data_sync.value = 1
        self.dut.io_max_time_sync.value = 0

        # FFT module
        self.fft_sim = FFT_Sim(dut.rst_area_acq.fft_inst, 12, 1, store=True)
        self.fft_sim.log.setLevel(logging.WARNING)

        self.host_mac = host_mac
        self.device_mac = device_mac
        self.host_ip = host_ip
        self.device_ip = device_ip

        # 200 MHz logic clock
        cocotb.start_soon(Clock(dut.clk, 5, units="ns").start())

        # 125 MHz ethernet clock
        cocotb.start_soon(Clock(dut.io_gtx_clk, 8, units="ns").start())

        # no mii_tx_clk, only supports 1G
        self.phy = GmiiPhy(
            dut.io_gmii_gmii_txd,
            dut.io_gmii_gmii_tx_er,
            dut.io_gmii_gmii_tx_en,
            dut.io_gmii_gmii_tx_clk,
            dut.io_gtx_clk,
            dut.io_gmii_gmii_rxd,
            dut.io_gmii_gmii_rx_er,
            dut.io_gmii_gmii_rx_dv,
            dut.io_gmii_gmii_rx_clk,
            reset=dut.io_gtx_rst,
        )
        self.phy.tx.log.setLevel(logging.WARNING)
        self.phy.rx.log.setLevel(logging.WARNING)

        self.rx_queue = Queue()
        self.tx_queue = Queue()

        self._run_cr = cocotb.start_soon(self._run())

    async def reset(self, delay=5):
        self.dut.reset.value = 0
        self.dut.io_gtx_rst.value = 0
        await ClockCycles(self.dut.clk, delay)
        self.dut.reset.value = 1
        self.dut.io_gtx_rst.value = 1
        await ClockCycles(self.dut.clk, delay)
        self.dut.reset.value = 0
        self.dut.io_gtx_rst.value = 0
        await ClockCycles(self.dut.clk, delay)

    async def _send_packet(self, pkt: bytes):
        frame = GmiiFrame.from_payload(pkt)
        await self.phy.rx.send(frame)

    async def send_udp_frame(self, data: bytes, source_port: int, dest_port: int):
        eth = Ether(src=self.host_mac, dst=self.device_mac)
        ip = IP(src=self.host_ip, dst=self.device_ip)
        udp = UDP(sport=source_port, dport=dest_port)
        pkt = eth / ip / udp / data

        await self.tx_queue.put(pkt.build())

    async def get_packet(self) -> Ether:
        return await with_timeout(self.rx_queue.get(), 100, "us")

    async def axil_write(self, addr, data):
        cmd = bytearray()

        cmd.append(0x80)
        cmd.extend([0, 0])
        cmd.extend(int.to_bytes(addr, 4, "little"))  # addr
        cmd.extend(int.to_bytes(data, 4, "little"))  # data
        cmd.insert(0, 1)  # Last byte

        await self.send_udp_frame(cmd, 12345, 1000)

    async def axil_read(self, addr):
        cmd = bytearray()

        cmd.append(0x00)
        cmd.extend([0, 0])
        cmd.extend(int.to_bytes(addr, 4, "little"))  # addr
        cmd.insert(0, 1)  # Last byte

        await self.send_udp_frame(cmd, 12345, 1000)
        # TODO: get reply

    async def send_samples(self, samples):
        # Normalize - scaling optimized for SNR
        samples /= np.max(np.abs(samples))
        samples *= 127

        # Repeat
        times_single = np.arange(4092)
        times = np.tile(times_single, int(len(samples) / 4092) + 1)
        times = times.astype(np.uint16)[0 : len(samples)]

        # Convert to 4 bit format
        samples_re = samples.real.astype(np.int8).astype(np.uint8) >> 6
        samples_im = samples.imag.astype(np.int8).astype(np.uint8) >> 6
        bits = samples_re | (samples_im << 2) | (times << 4)
        bits = np.array(bits, dtype=np.uint16)

        # Get quantized samples
        samples_re = (samples_re << 6).astype(np.int8) | 0b100000
        samples_im = (samples_im << 6).astype(np.int8) | 0b100000

        samples_quant = samples_re + samples_im * 1j
        samples_quant /= 128

        # SpinalHDL width adapter puts lower bits in first
        bits_bytes = np.empty(len(bits) * 2, dtype=np.uint8)
        bits_bytes[::2] = bits & 0xFF
        bits_bytes[1::2] = bits >> 8

        for i in range(0, len(bits_bytes), 500):
            data = bytearray()
            data.extend(bits_bytes[i : i + 500])
            data.insert(0, 0)  # last = 0
            await self.send_udp_frame(data, 12345, 1010)

    async def _run(self):
        while True:
            await ClockCycles(self.dut.clk, 10)

            if not self.phy.tx.empty():
                frame = await self.phy.tx.recv()
                pkt = Ether(frame.data[8:])

                # Handle ARP
                if ARP in pkt:
                    self.dut._log.info(f"Got ARP packet: {pkt}")

                    reply = Ether(src=self.host_mac, dst=self.device_mac)
                    reply = reply / ARP(
                        op="is-at",
                        hwsrc=self.host_mac,
                        psrc=self.host_ip,
                        hwdst=self.device_mac,
                        pdst=self.device_ip,
                    )

                    await self._send_packet(reply.build())
                else:
                    await self.rx_queue.put(pkt)

            if not self.tx_queue.empty():
                await self._send_packet(self.tx_queue.get_nowait())


@cocotb.test
async def test_ethtb(dut):
    SRC_MAC = "01:23:45:67:89:ab"
    DST_MAC = "00:00:01:00:00:02"
    SRC_IP = "10.0.0.1"
    DST_IP = "10.0.0.2"

    N = 50000

    tb = TB(dut, SRC_MAC, DST_MAC, SRC_IP, DST_IP)
    await tb.reset()
    await ClockCycles(dut.clk, 50)

    # Soft reset
    await tb.axil_write(0x00, 0x00)
    await Timer(8, "us")

    # Test AXIL read
    await tb.axil_read(0xFFC)

    # Activate MAX2769 IQ interface
    await tb.send_udp_frame(bytes([0, 0]), 12345, 1030)

    # Wait until steady state
    await Timer(100, "us")

    # Attempt to send AXIL read request
    await tb.axil_read(0xFFC)

    await Timer(100, "us")

    # Print all received packets
    while not tb.rx_queue.empty():
        print(tb.rx_queue.get_nowait())


if __name__ == "__main__":
    verilog_eth_path = Path("../../../verilog-ethernet/rtl")
    verilog_axi_path = Path("../../../verilog-ethernet/lib/axis/rtl")

    eth_files = [x.name for x in verilog_eth_path.glob("*") if x.is_file()]
    axi_files = [x.name for x in verilog_axi_path.glob("*.v") if x.is_file()]

    verilog_sources = []
    verilog_sources.extend([f"verilog-ethernet/rtl/{x}" for x in eth_files])
    verilog_sources.extend([f"verilog-ethernet/lib/axis/rtl/{x}" for x in axi_files])
    verilog_sources.append("hw/verilog/XilinxFFT.v")

    test_runner.run_wrapper(
        top_level="EthernetTestbench",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
        verilog_sources=verilog_sources,
    )
