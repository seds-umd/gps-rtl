from migen import Signal, ClockDomain

from litex.build.generic_platform import Pins, Subsignal, IOStandard, Misc
from litex.build.xilinx import Xilinx7SeriesPlatform
from litex.build.openocd import OpenOCD

from litex.gen import LiteXModule

from litex.soc.cores.clock.xilinx_s7 import S7MMCM


class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.cd_sys = ClockDomain()

        self.pll = pll = S7MMCM(speedgrade=-1)
        self.comb += pll.reset.eq(self.rst)

        pll.register_clkin(platform.request("clk100"), 100e6)
        pll.create_clkout(self.cd_sys, sys_clk_freq)
        platform.add_false_path_constraints(self.cd_sys.clk, pll.clkin)


# IOs ----------------------------------------------------------------------------------------------

_io = [
    # Clk / Rst
    ("clk100", 0, Pins("R2"), IOStandard("SSTL135")),
    ("cpu_reset", 0, Pins("C18"), IOStandard("LVCMOS33")),
    (
        "max2769",
        0,
        Subsignal("sclk", Pins("L1")),
        Subsignal("cs", Pins("N1")),
        Subsignal("sdata", Pins("M1")),
        Subsignal("clk_ser", Pins("G4")),
        Subsignal("data_in", Pins("F1")),
        Subsignal("data_sync", Pins("F3")),
        Subsignal("time_sync", Pins("F2")),
        IOStandard("LVCMOS33"),
    ),
    ("misc_io", 0, Pins("F13 F14 G11 G14 H12 L14 M13 N10 N11 P10 P11 P12 P13")),
]


# Platform -----------------------------------------------------------------------------------------

# TODO: figure out real clock frequency


class Platform(Xilinx7SeriesPlatform):
    default_clk_name = "clk100"
    default_clk_period = 1e9 / 100e6

    def __init__(self, variant="s25", toolchain="vivado"):
        device = {"s12": "xc7s15ftgb196-1", "s25": "xc7s25ftgb196-1"}[variant]
        Xilinx7SeriesPlatform.__init__(self, device, _io, toolchain=toolchain)

    def do_finalize(self, fragment):
        Xilinx7SeriesPlatform.do_finalize(self, fragment)
        self.add_period_constraint(
            self.lookup_request("clk100", loose=True), 1e9 / 100e6
        )
