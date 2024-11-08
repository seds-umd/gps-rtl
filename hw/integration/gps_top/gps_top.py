#!/usr/bin/env python3

from migen import *

from litex.build.openfpgaloader import OpenFPGALoader

from litex.soc.integration.soc_core import SoCCore
from litex.soc.integration.builder import Builder

import gps_board


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
        platform.add_sources("../../gen", "GpsTop.v")

        self.crg = gps_board._CRG(platform, sys_clk_freq)

        max_interface = platform.request("max2769")
        misc_io = platform.request("misc_io")

        ios = dict(
            i_clk=ClockSignal("sys"),
            i_reset=ResetSignal("sys"),
            i_io_clk_ser=max_interface.clk_ser,
            i_io_data_in=max_interface.data_in,
            i_io_data_sync=max_interface.data_sync,
            i_io_time_sync=max_interface.time_sync,
            # o_io_spi_cs=max_interface.cs,
            # o_io_spi_sclk=max_interface.sclk,
            # o_io_spi_sdata=max_interface.sdata,
            o_io_debug_out=misc_io,
        )
        self.specials += Instance("GpsTop", **ios)

        self.platform.add_ip("fft.tcl")
        self.platform.add_ip("../eth_top/cordic.tcl")


def main():
    from litex.build.parser import LiteXArgumentParser

    platform = gps_board.Platform("s50")

    parser = LiteXArgumentParser(platform=platform, description="SATFAB GPS Board")

    args = parser.parse_args()

    module = UartTop(platform=platform)

    builder = Builder(
        module,
        output_dir="build",
        compile_gateware=True,
    )

    if args.build:
        builder.build(**parser.toolchain_argdict)

    # WARNING: IO settings not final, double check before loading
    # if args.load:
    #     prog = OpenFPGALoader(board="basys3", freq=3e6)
    #     prog.load_bitstream(builder.get_bitstream_filename(mode="sram"))


if __name__ == "__main__":
    main()
