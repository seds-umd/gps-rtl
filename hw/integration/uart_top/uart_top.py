#!/usr/bin/env python3

from migen import *

from litex.build.openfpgaloader import OpenFPGALoader
from litex.build.generic_platform import Subsignal, Pins, IOStandard

from litex_boards.platforms import digilent_basys3
from litex_boards.targets.digilent_basys3 import _CRG

from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder


class UartTop(SoCCore):
    def __init__(
        self,
        platform,
        sys_clk_freq=50e6,
    ):
        SoCCore.__init__(
            self,
            platform,
            sys_clk_freq,
            cpu_type=None,
            integrated_sram_size=0,
            with_timer=False,
            with_uart=False,
        )

        self.platform = platform

        # Verilog sources
        platform.add_sources("../../gen", "UartTop.v")
        platform.add_source_dir("../../verilog")

        self.crg = _CRG(platform, sys_clk_freq)

        platform.add_extension([(
            "max_interface",
            0,
            Subsignal("sclk", Pins("pmodc:6")),
            Subsignal("cs", Pins("pmodc:7")),
            Subsignal("sdata", Pins("pmodc:5")),
            Subsignal("clk_ser", Pins("pmodc:2")),
            Subsignal("data_in", Pins("pmodc:3")),
            Subsignal("data_sync", Pins("pmodc:0")),
            Subsignal("time_sync", Pins("pmodc:1")),
            IOStandard("LVCMOS33"),
        )])

        max_interface = platform.request("max_interface")
        uart = platform.request("serial")

        ios = dict(
            i_clk=ClockSignal("sys"),
            i_reset=ResetSignal("sys"),
            i_io_clk_ser=max_interface.clk_ser,
            i_io_data_in=max_interface.data_in,
            i_io_data_sync=max_interface.data_sync,
            i_io_time_sync=max_interface.time_sync,
            o_io_SCLK=max_interface.sclk,
            o_io_CS=max_interface.cs,
            o_io_SDATA=max_interface.sdata,
            o_io_uart_txd=uart.tx,
            i_io_uart_rxd=uart.rx,
        )
        self.specials += Instance("UartTop", **ios)


def main():
    from litex.build.parser import LiteXArgumentParser

    platform = digilent_basys3.Platform()

    parser = LiteXArgumentParser(
        platform=platform, description="LiteX SoC on AliExpress STLV7325 V1"
    )

    args = parser.parse_args()

    module = UartTop(platform=platform)

    builder = Builder(
        module,
        output_dir="build",
        compile_gateware=True,
    )

    if args.build:
        builder.build(**parser.toolchain_argdict)

    if args.load:
        prog = OpenFPGALoader(board="basys3", freq=3e6)
        prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))


if __name__ == "__main__":
    main()
