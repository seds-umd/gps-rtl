#!/usr/bin/env python3

from migen import Signal, ClockDomain, Instance, ClockSignal, ResetSignal

from litex.soc.integration.builder import Builder
from litex_boards.platforms import digilent_arty
from litex.build.generic_platform import GenericPlatform, IOStandard, Pins, Subsignal
from litex.soc.cores.clock import S7PLL
from litex.gen import LiteXModule
from litex.soc.integration.soc_core import SoCCore
from litex.build.openfpgaloader import OpenFPGALoader


class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq, with_rst=True):
        self.rst = Signal()
        self.cd_sys = ClockDomain()
        self.cd_eth = ClockDomain()

        # Clk/Rst.
        clk100 = platform.request("clk100")
        rst = ~platform.request("cpu_reset") if with_rst else 0

        # PLL.
        self.pll = pll = S7PLL(speedgrade=-1)
        self.comb += pll.reset.eq(rst | self.rst)
        pll.register_clkin(clk100, 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        pll.create_clkout(self.cd_eth, 25e6)
        self.comb += platform.request("eth_ref_clk").eq(self.cd_eth.clk)
        platform.add_false_path_constraints(
            self.cd_sys.clk, pll.clkin
        )  # Ignore sys_clk to pll.clkin path created by SoC's rst.


class EthernetTestbench(SoCCore):
    def __init__(self, platform: GenericPlatform, sys_clk_freq=200e6):
        SoCCore.__init__(
            self,
            platform,
            sys_clk_freq,
            # Disable CPU stuff
            cpu_type=None,
            integrated_sram_size=0,
            with_timer=False,
            with_uart=False,
        )

        self.platform = platform

        # Verilog sources
        platform.add_sources("../../gen", "sources.v", "EthernetCiTestbench.v")

        # Ethernet setup
        eth_clocks = platform.request("eth_clocks")
        eth_pads = platform.request("eth")

        # print(eth_clocks)
        # print(eth_pads)

        self.crg = _CRG(self.platform, sys_clk_freq)

        # Maybe?
        # self.platform.add_false_path_constraints(self.crg.cd_sys.clk, eth_clocks.rx)

        # MAX2769 pins
        pins = {
            "sclk": "K15",
            "cs": "J15",
            "sdata": "J18",
            "clk_ser": "D15",
            "data_in": "C15",
            "data_sync": "E15",
            "time_sync": "E16",
        }
        pin_setup = (
            ["max", 0]
            + [Subsignal(k, Pins(v)) for k, v in pins.items()]
            + [IOStandard("LVCMOS33")]
        )
        platform.add_extension([pin_setup])

        max2769 = platform.request("max")

        # Test IP
        ios = {
            "i_clk": ClockSignal("sys"),
            "i_reset": ResetSignal("sys"),

            # Ethernet
            "i_io_mii_mii_rx_clk": eth_clocks.rx,
            "i_io_mii_mii_rxd": eth_pads.rx_data,
            "i_io_mii_mii_rx_dv": eth_pads.rx_dv,
            "i_io_mii_mii_rx_er": eth_pads.rx_er,
            "i_io_mii_mii_tx_clk": eth_clocks.tx,
            "o_io_mii_mii_txd": eth_pads.tx_data,
            "o_io_mii_mii_tx_en": eth_pads.tx_en,
            # "o_io_mii_mii_tx_er": eth_pads.tx_er,

            # MAX2769
            "o_io_spi_cs": max2769.cs,
            "o_io_spi_sclk": max2769.sclk,
            "o_io_spi_sdata": max2769.sdata,
            "i_io_max_clk_ser": max2769.clk_ser,
            "i_io_max_data_in": max2769.data_in,
            "i_io_max_data_sync": max2769.data_sync,
            "i_io_max_time_sync": max2769.time_sync,
        }

        self.specials += Instance("EthernetCiTestbench", **ios)

        # Xilinx IP
        self.platform.add_ip("../fft_fast.tcl")
        # self.platform.add_ip("../cordic_sincos.tcl")
        # self.platform.add_ip("../cordic_atan.tcl")


def main():
    from litex.build.parser import LiteXArgumentParser

    parser = LiteXArgumentParser(
        platform=digilent_arty.Platform, description="LiteX SoC on Arty A7."
    )

    parser.add_target_argument("--flash", action="store_true", help="Flash bitstream.")
    parser.add_target_argument(
        "--variant", default="a7-100", help="Board variant (a7-35 or a7-100)."
    )
    args = parser.parse_args()

    platform = digilent_arty.Platform(args.variant)

    module = EthernetTestbench(
        platform,
        sys_clk_freq=100e6,
    )

    builder = Builder(module, output_dir="build", compile_gateware=True)
    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = OpenFPGALoader("arty_a7_100t")
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))

    if args.flash:
        prog = OpenFPGALoader("arty_a7_100t")
        prog.flash(0, builder.get_bitstream_filename(mode="flash"))


if __name__ == "__main__":
    main()
