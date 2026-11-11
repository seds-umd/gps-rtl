#!/usr/bin/env python3
"""GpsSelfTest on a Digilent Arty S7.

The acquisition core with the real Xilinx FFT, fed by the on-chip MAX2769
emulator, reporting results on the board's USB serial port. Nothing needs to be
plugged into the PMODs. See scripts/arty_selftest.py for the host side.

    sbt "runMain gps.GpsSelfTestVerilog"    # from the repository root, first
    ./arty_s7.py --build                    # needs Vivado on PATH
    ./arty_s7.py --load                     # program over the USB cable
    ./arty_s7.py --detect                   # show which FPGA is on the cable

Use --variant s7-25 for the smaller board. Loading goes through Vivado's
hardware manager so the stock Digilent/FTDI cable drivers work on Windows.
"""

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

from migen import ClockDomain, ClockSignal, Instance, ResetSignal, Signal

from litex.gen import LiteXModule
from litex.soc.cores.clock import S7MMCM
from litex.soc.integration.builder import Builder
from litex.soc.integration.soc_core import SoCCore

from litex_boards.platforms import digilent_arty_s7

HERE = Path(__file__).resolve().parent
GEN = HERE.parent.parent / "gen"

SYS_CLK_FREQ = 50e6  # Must match Config.scala
SERIAL_CLK_FREQ = 16.368e6  # Four serial clocks per 4.092 Msps sample, as from a MAX2769
CROSSING_MAX_DELAY_NS = 8.0  # Well under one period of either clock (20 ns and 61 ns)
PARTS = {"s7-50": "xc7s50", "s7-25": "xc7s25"}


class _CRG(LiteXModule):
    def __init__(self, platform, sys_clk_freq):
        self.rst = Signal()
        self.cd_sys = ClockDomain()
        self.cd_ser = ClockDomain(reset_less=True)

        clk100 = platform.request("clk100")
        rst_n = platform.request("cpu_reset_n")

        self.mmcm = mmcm = S7MMCM(speedgrade=-1)
        self.comb += mmcm.reset.eq(~rst_n | self.rst)
        mmcm.register_clkin(clk100, 100e6)
        # Only CLKOUT0 has a fractional divider, so the odd frequency goes first.
        mmcm.create_clkout(self.cd_ser, SERIAL_CLK_FREQ, margin=2e-3, with_reset=False)
        mmcm.create_clkout(self.cd_sys, sys_clk_freq, margin=0)
        platform.add_false_path_constraints(self.cd_sys.clk, mmcm.clkin)
        # The two domains only meet through the asynchronous sample FIFO,
        # synchronizers and settings that are static while the core runs. Bound
        # the delay of those paths instead of cutting them: the FIFO's Gray-code
        # pointers are only safe if their bits arrive well within one clock of
        # each other, and a plain asynchronous clock group would not check that.
        # Keep both net names through synthesis so the constraints below can find them.
        self.cd_sys.clk.attr.add("keep")
        self.cd_ser.clk.attr.add("keep")
        for source, destination in ((self.cd_sys, self.cd_ser), (self.cd_ser, self.cd_sys)):
            platform.toolchain.pre_placement_commands.add(
                "set_max_delay -datapath_only %.1f "
                "-from [get_clocks -of [get_nets {source}]] -to [get_clocks -of [get_nets {destination}]]"
                % CROSSING_MAX_DELAY_NS,
                source=source.clk, destination=destination.clk,
            )


class GpsSelfTestSoC(SoCCore):
    def __init__(self, platform, sys_clk_freq=SYS_CLK_FREQ):
        SoCCore.__init__(
            self,
            platform,
            sys_clk_freq,
            cpu_type=None,
            integrated_sram_size=0,
            with_timer=False,
            with_uart=False,
        )

        self.crg = _CRG(platform, sys_clk_freq)

        source = GEN / "GpsSelfTest.v"
        if not source.exists():
            raise SystemExit(f'{source} is missing. Run: sbt "runMain gps.GpsSelfTestVerilog"')
        newest = max(p.stat().st_mtime for p in (GEN.parent / "spinal").rglob("*.scala"))
        if newest > source.stat().st_mtime:
            raise SystemExit(f'{source} is older than the Scala sources. Run: sbt "runMain gps.GpsSelfTestVerilog"')
        platform.add_source(str(source))
        # The XilinxFFT module comes from the vendor core, not hw/verilog.
        platform.add_ip(str(HERE.parent / "eth_top" / "fft.tcl"))

        serial = platform.request("serial")
        self.specials += Instance(
            "GpsSelfTest",
            i_clk=ClockSignal("sys"),
            i_reset=ResetSignal("sys"),
            i_io_clk_ser=ClockSignal("ser"),
            o_io_uart_txd=serial.tx,
            i_io_uart_rxd=serial.rx,
            o_io_leds=platform.request_all("user_led"),
        )


def find_vivado():
    vivado = shutil.which("vivado.bat" if sys.platform == "win32" else "vivado") or shutil.which("vivado")
    if vivado is None:
        raise SystemExit("Vivado is not on PATH.")
    return vivado


def build_bitstream(gateware, name):
    """Run the project LiteX generated.

    Vivado is started directly instead of through LiteX's build script: on
    Windows that script is a batch file found through the current directory,
    which fails when NoDefaultCurrentDirectoryInExePath is set.
    """
    bitstream = gateware / f"{name}.bit"
    bitstream.unlink(missing_ok=True)
    done = subprocess.run(
        [find_vivado(), "-mode", "batch", "-nojournal", "-log", f"{name}_vivado.log", "-source", f"{name}.tcl"],
        cwd=gateware,
    )
    if done.returncode != 0 or not bitstream.exists():
        raise SystemExit(f"Vivado build failed; see {gateware / (name + '_vivado.log')}")


def run_vivado_tcl(commands):
    """Run Tcl in Vivado batch mode and return its output."""
    vivado = find_vivado()
    # Not a temporary directory: connect_hw_server leaves hw_server running with
    # this as its working directory, and Windows cannot delete a directory in use.
    work = HERE / "build"
    work.mkdir(exist_ok=True)
    script = work / "hardware.tcl"
    script.write_text(commands, encoding="ascii")
    done = subprocess.run(
        [vivado, "-mode", "batch", "-nojournal", "-nolog", "-notrace", "-source", str(script)],
        cwd=work, capture_output=True, text=True,
    )
    if done.returncode != 0:
        raise SystemExit(f"Vivado failed:\n{done.stdout}\n{done.stderr}")
    return done.stdout


OPEN_TARGET = """
open_hw_manager
connect_hw_server
open_hw_target
set device [lindex [get_hw_devices] 0]
current_hw_device $device
puts "CABLE_DEVICE [get_property PART $device]"
"""

CLOSE_TARGET = """
close_hw_target
disconnect_hw_server
close_hw_manager
"""


def detect():
    """Part name of the first FPGA on the JTAG cable, for example xc7s50."""
    output = run_vivado_tcl(OPEN_TARGET + CLOSE_TARGET)
    match = re.search(r"^CABLE_DEVICE (\S+)", output, re.MULTILINE)
    if not match:
        raise SystemExit(f"No FPGA found on the cable:\n{output}")
    return match.group(1)


def load(bitstream, variant):
    """Program the FPGA (volatile: the board returns to its flash image on power-up)."""
    path = Path(bitstream).resolve().as_posix()
    output = run_vivado_tcl(
        OPEN_TARGET
        + f"""
if {{![string match "{PARTS[variant]}*" [get_property PART $device]]}} {{
    puts "WRONG_DEVICE"
    exit 2
}}
set_property PROBES.FILE {{}} $device
set_property PROGRAM.FILE {{{path}}} $device
program_hw_devices $device
refresh_hw_device $device
puts "DONE_PIN [get_property REGISTER.CONFIG_STATUS.BIT14_DONE_PIN $device]"
"""
        + CLOSE_TARGET
    )
    if "DONE_PIN 1" not in output:
        raise SystemExit(f"The FPGA did not report DONE after programming:\n{output}")
    print(f"Programmed {PARTS[variant]} with {bitstream}")


def summarize(gateware, name):
    """Pull the numbers worth recording out of the Vivado reports."""
    summary = {"bitstream": str(gateware / f"{name}.bit")}
    bitstream = gateware / f"{name}.bit"
    if bitstream.exists():
        summary["bitstream_sha256"] = hashlib.sha256(bitstream.read_bytes()).hexdigest()

    timing = gateware / f"{name}_timing.rpt"
    if timing.exists():
        text = timing.read_text(errors="replace")
        match = re.search(r"WNS\(ns\)\s+TNS\(ns\).*?\n\s*-+.*?\n\s*(-?[\d.]+)\s+(-?[\d.]+)\s+\d+\s+\d+\s+(-?[\d.]+)\s+(-?[\d.]+)", text, re.S)
        if match:
            wns, tns, whs, ths = (float(x) for x in match.groups())
            summary.update(setup_wns_ns=wns, setup_tns_ns=tns, hold_whs_ns=whs, hold_ths_ns=ths)
            summary["timing_met"] = wns >= 0 and whs >= 0
        summary["all_registers_clocked"] = "There are 0 register/latch pins with no clock" in text
    # Anything other than a positive reading counts as a failure.
    summary.setdefault("timing_met", False)

    utilization = gateware / f"{name}_utilization_place.rpt"
    if utilization.exists():
        text = utilization.read_text(errors="replace")
        for label, key in (
            ("Slice LUTs", "luts"), ("Slice Registers", "registers"),
            ("Block RAM Tile", "block_ram_tiles"), ("DSPs", "dsps"),
        ):
            match = re.search(rf"\|\s*{label}\s*\|\s*([\d.]+)\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|", text)
            if match:
                summary[key] = {"used": float(match.group(1)), "available": float(match.group(2)),
                                "percent": float(match.group(3))}
    return summary


def main():
    from litex.build.parser import LiteXArgumentParser

    parser = LiteXArgumentParser(platform=digilent_arty_s7.Platform, description=__doc__.splitlines()[0])
    parser.add_target_argument("--variant", default="s7-50", choices=sorted(PARTS), help="Board variant.")
    parser.add_target_argument("--detect", action="store_true", help="Report the FPGA on the cable and exit.")
    args = parser.parse_args()

    if args.detect:
        print(f"FPGA on the cable: {detect()}")
        return

    platform = digilent_arty_s7.Platform(variant=args.variant)
    soc = GpsSelfTestSoC(platform)
    output_dir = HERE / "build" / args.variant
    # LiteX writes the project (Verilog top, constraints, Tcl); Vivado is run below.
    builder = Builder(soc, output_dir=str(output_dir), compile_gateware=False)
    builder.build(**parser.toolchain_argdict)

    gateware = output_dir / "gateware"
    if args.build:
        build_bitstream(gateware, platform.name)
        summary = summarize(gateware, platform.name)
        (output_dir / "summary.json").write_text(json.dumps(summary, indent=2))
        print(json.dumps(summary, indent=2))
        if not summary["timing_met"]:
            raise SystemExit("Timing was not met or could not be read; do not trust this bitstream.")

    if args.load:
        load(gateware / f"{platform.name}.bit", args.variant)


if __name__ == "__main__":
    main()
