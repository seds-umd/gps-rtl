#!/usr/bin/env python3
"""Host side of the GpsSelfTest board design.

Programs the on-chip MAX2769 emulator with known synthetic satellite signals,
reads the acquisition results the FPGA reports over its USB serial port and
checks each one against what was programmed.

    python scripts/arty_selftest.py                 # find the board, run every scenario
    python scripts/arty_selftest.py --port COM4 --report selftest.md
    python scripts/arty_selftest.py --soak 300      # also watch for sample overflow for 5 minutes

The protocol and checking functions at the top have no serial-port dependency,
so the GpsSelfTest simulation testbench uses the same code.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import max_emulator as model  # noqa: E402

# Register map; hw/spinal/gps/GpsSelfTest.scala has the same addresses.
REG_CTRL = 0x00
REG_ID = 0x01
REG_STATUS = 0x02
REG_QUANT = 0x03
REG_SEED = 0x04
REG_INFO = 0x05
REG_CHANNEL_BASE = 0x10
REG_CHANNEL_STRIDE = 4

ID_WORD = 0x47505331  # "GPS1"
SATELLITES = 32


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------


@dataclass
class Reply:
    kind: str  # "w", "q", "i" or "e"
    address: Optional[int] = None
    value: Optional[int] = None


@dataclass
class Result:
    sv: int
    freq_offset: int  # Signed, in fine bins of 4.092e6 / (4096 * 8) Hz
    phase_offset: int  # Samples, 0 to 4091
    metric: int  # Saturating detection metric, not a calibrated dB value
    overflow: bool

    @property
    def doppler_hz(self) -> float:
        return self.freq_offset * model.FINE_BIN_HZ


def write_command(address: int, value: int) -> bytes:
    return f"W{address:02X}{value & 0xFFFFFFFF:08X}\n".encode("ascii")


def read_command(address: int) -> bytes:
    return f"Q{address:02X}\n".encode("ascii")


def identify_command() -> bytes:
    return b"?\n"


def parse_line(line: Union[str, bytes]) -> Union[Reply, Result, None]:
    """Decode one line from the board. Blank lines give None; bad ones raise ValueError."""
    if isinstance(line, bytes):
        line = line.decode("ascii", errors="replace")
    line = line.strip()
    if not line:
        return None
    kind, body = line[0], line[1:]
    try:
        if kind == "R" and len(body) == 11:
            freq = int(body[2:5], 16)
            return Result(
                sv=int(body[0:2], 16),
                freq_offset=freq - 4096 if freq >= 2048 else freq,
                phase_offset=int(body[5:8], 16),
                metric=int(body[8:10], 16),
                overflow=bool(int(body[10], 16) & 1),
            )
        if kind in "wqi" and len(body) == 10:
            return Reply(kind, int(body[0:2], 16), int(body[2:10], 16))
        if kind == "e" and not body:
            return Reply("e")
    except ValueError:
        pass
    raise ValueError(f"Unrecognized line from board: {line!r}")


# ---------------------------------------------------------------------------
# Scenarios and checks
# ---------------------------------------------------------------------------


@dataclass
class Scenario:
    name: str
    channels: List[model.Channel]
    noise_gain: int = 0
    threshold: int = 64
    seed: int = 1
    # A present satellite must beat every absent one by this factor and reach min_metric.
    separation: float = 4.0
    min_metric: int = 9
    # Half a chip. The coarse search runs a 4096-point FFT over a code that
    # repeats every 4092 samples, so when the code boundary falls mid-window the
    # correlation peak is a flat top five samples wide and the reported phase
    # can land anywhere on it.
    phase_tolerance: int = 2
    # Scenarios that characterize rather than gate (for example signals near the noise floor).
    informational: bool = False
    note: str = ""

    def present(self) -> Dict[int, model.Channel]:
        return {c.sv: c for c in self.channels if c.enable}


def scenario_writes(scenario: Scenario, channel_count: int) -> List[Tuple[int, int]]:
    """Register writes that program a scenario. Send them while the core is stopped."""
    if len(scenario.channels) > channel_count:
        raise ValueError(f"{scenario.name}: {len(scenario.channels)} channels, board has {channel_count}")
    writes = [
        (REG_QUANT, (scenario.noise_gain & 0xFF) | ((scenario.threshold & 0xFF) << 8)),
        (REG_SEED, scenario.seed & 0xFFFFFFFF),
    ]
    for k in range(channel_count):
        channel = scenario.channels[k] if k < len(scenario.channels) else model.Channel(sv=1, enable=False, amplitude=0)
        if not 1 <= channel.sv <= SATELLITES:
            raise ValueError(f"{scenario.name}: satellite {channel.sv} is out of range")
        if not 0 <= channel.code_phase < model.PERIOD:
            raise ValueError(f"{scenario.name}: code phase {channel.code_phase} is out of range")
        base = REG_CHANNEL_BASE + REG_CHANNEL_STRIDE * k
        writes.append((base + 0, channel.sv | (int(channel.enable) << 8) | ((channel.amplitude & 0xFF) << 16)))
        writes.append((base + 1, channel.carrier_inc & 0xFFFFFFFF))
        writes.append((base + 2, channel.code_phase))
    return writes


def check_order(results: Sequence[Result], first_sv: int = 1) -> List[str]:
    """Results must enumerate the satellites in order, wrapping after 32."""
    problems = []
    for index, result in enumerate(results):
        expected = (first_sv - 1 + index) % SATELLITES + 1
        if result.sv != expected:
            problems.append(f"result {index} is satellite {result.sv}, expected {expected}")
            break
    return problems


def check_results(scenario: Scenario, results: Iterable[Result]) -> List[str]:
    """Compare acquisition results with what the emulator was programmed to send."""
    problems = []
    results = list(results)
    present = scenario.present()
    absent_metrics = [r.metric for r in results if r.sv not in present]
    absent_peak = max(absent_metrics) if absent_metrics else 0

    for result in results:
        if result.overflow:
            problems.append(f"satellite {result.sv}: sample overflow flag is set")
        channel = present.get(result.sv)
        if channel is None:
            continue
        expected_freq = channel.expected_freq_offset
        if abs(result.freq_offset - expected_freq) > 1:
            problems.append(f"satellite {result.sv}: freq_offset {result.freq_offset}, expected {expected_freq:g}")
        error = (result.phase_offset - channel.code_phase) % model.PERIOD
        if min(error, model.PERIOD - error) > scenario.phase_tolerance:
            problems.append(f"satellite {result.sv}: phase_offset {result.phase_offset}, expected {channel.code_phase}")
        if result.metric < scenario.min_metric:
            problems.append(f"satellite {result.sv}: metric {result.metric} is below {scenario.min_metric}")
        if absent_metrics and result.metric < scenario.separation * absent_peak:
            problems.append(
                f"satellite {result.sv}: metric {result.metric} is not {scenario.separation:g}x "
                f"the strongest absent satellite ({absent_peak})"
            )

    seen = {r.sv for r in results}
    for sv in present:
        if sv not in seen:
            problems.append(f"satellite {sv}: no result received")
    return problems


def fine(bin_number: float) -> int:
    """carrier_inc for a Doppler given in fine bins (124.9 Hz each)."""
    return int(round(bin_number * model.INC_PER_FINE_BIN))


def hardware_scenarios() -> List[Scenario]:
    """Signals for the full +/-24 coarse bin search of the hardware build."""
    scenarios = [
        Scenario("baseline: SV 2, +1.0 kHz, phase 37", [model.Channel(2, 37, fine(8))]),
        Scenario("zero Doppler, zero phase: SV 1", [model.Channel(1, 0, 0)]),
        Scenario("positive search edge: SV 32, +23.0 kHz", [model.Channel(32, 4091, fine(184))]),
        Scenario("negative search edge: SV 17, -23.0 kHz", [model.Channel(17, 2046, fine(-184))]),
        Scenario("Doppler between fine bins: SV 21, bin 10.5", [model.Channel(21, 500, fine(10.5))]),
        Scenario(
            "two satellites, equal power: SV 5 and SV 23",
            [model.Channel(5, 100, fine(20), 68), model.Channel(23, 3000, fine(-60), 68)],
        ),
        Scenario(
            "two satellites, 12 dB apart, no noise: SV 12 and SV 30",
            [model.Channel(12, 2222, fine(-33), 96), model.Channel(30, 1234, fine(77), 24)],
            informational=True,
            note="Without noise to dither the 2-bit quantizer the strong signal partly captures it; "
                 "recorded to show the weak one is still found.",
        ),
    ]

    # The FFT works on 4096 points but a code period is 4092 samples; the core
    # maps between them in five steps. Probe both sides of every step and the wrap.
    for phase in (1, 818, 819, 1636, 1637, 2454, 2455, 3273, 3274, 4090):
        scenarios.append(Scenario(f"code phase {phase}: SV 9", [model.Channel(9, phase, fine(-12))]))

    # Noise. With noise_gain 87 the per-rail noise sigma is about 12,860 internal
    # units, so amplitude A gives C/N0 = 20*log10(A*127/12860) - 3 + 66.1 dB-Hz.
    scenarios.append(
        Scenario(
            "noise, about 51 dB-Hz: SV 14",
            [model.Channel(14, 1500, fine(40), 26)],
            noise_gain=87, threshold=100, seed=0xC0FFEE, separation=1.5,
        )
    )
    scenarios.append(
        Scenario(
            "two satellites in noise, about 57 and 51 dB-Hz: SV 3 and SV 27",
            [model.Channel(3, 700, fine(-96), 52), model.Channel(27, 3300, fine(120), 26)],
            noise_gain=87, threshold=100, seed=0xBEEF, separation=1.5,
        )
    )
    # A single 1 ms coherent search needs roughly 15 dB after correlation, and
    # the 4096/4092 mismatch can cost up to 6 dB of that depending on where the
    # code boundary falls in the window. These two sit at and below that limit.
    for amplitude, cn0 in ((13, 45), (7, 40)):
        scenarios.append(
            Scenario(
                f"noise, about {cn0} dB-Hz: SV 14",
                [model.Channel(14, 1500, fine(40), amplitude)],
                noise_gain=87, threshold=100, seed=0xC0FFEE, informational=True,
                note="At or below the sensitivity of a single 1 ms search; recorded, not gated.",
            )
        )
    scenarios.append(
        Scenario(
            "noise only, no satellites",
            [], noise_gain=87, threshold=100, seed=0xC0FFEE, informational=True,
            note="Shows the metric the core reports when nothing is there.",
        )
    )
    return scenarios


# ---------------------------------------------------------------------------
# Serial port
# ---------------------------------------------------------------------------


def find_port() -> str:
    """The Arty's USB serial port: the UART side of its FT2232 (0403:6010)."""
    from serial.tools import list_ports

    ports = [p for p in list_ports.comports() if p.vid == 0x0403 and p.pid == 0x6010]
    if not ports:
        raise SystemExit("No Digilent/FTDI serial port found. Is the board connected with a data cable?")
    # The UART is the higher-numbered of the two interfaces. Sort numerically: "COM10" < "COM9" as text.
    def number(name: str) -> int:
        digits = "".join(ch for ch in name if ch.isdigit())
        return int(digits) if digits else 0

    return max((p.device for p in ports), key=number)


class Board:
    def __init__(self, port: str, baud: int = 115200, timeout: float = 2.0):
        import serial

        self.serial = serial.Serial(port, baud, timeout=0.05)
        self.timeout = timeout
        self.buffer = b""
        self.pending_results: List[Result] = []
        self.bad_lines: List[str] = []

    def close(self) -> None:
        self.serial.close()

    def _lines(self, deadline: float):
        while True:
            while b"\n" in self.buffer:
                raw, self.buffer = self.buffer.split(b"\n", 1)
                yield raw
            if time.monotonic() > deadline:
                return
            self.buffer += self.serial.read(256)

    def _next(self, deadline: float) -> Union[Reply, Result, None]:
        for raw in self._lines(deadline):
            try:
                parsed = parse_line(raw)
            except ValueError:
                self.bad_lines.append(raw.decode("ascii", errors="replace").strip())
                continue
            if parsed is not None:
                return parsed
        return None

    def command(self, data: bytes, kind: str) -> Reply:
        """Send a command and return its reply; result lines seen meanwhile are queued."""
        self.serial.write(data)
        deadline = time.monotonic() + self.timeout
        while True:
            parsed = self._next(deadline)
            if parsed is None:
                raise TimeoutError(f"No reply to {data!r}")
            if isinstance(parsed, Result):
                self.pending_results.append(parsed)
            elif parsed.kind == "e":
                raise RuntimeError(f"Board rejected {data!r}")
            elif parsed.kind == kind:
                return parsed

    def sync(self) -> None:
        """Stop the core and discard whatever was in flight, including a partial line."""
        # A line end cancels any half-received command (the board answers "e").
        self.serial.write(b"\n")
        time.sleep(0.1)
        self.serial.reset_input_buffer()
        self.buffer = b""
        self.write(REG_CTRL, 0, verify=False)
        time.sleep(0.1)
        self.serial.reset_input_buffer()
        self.buffer = b""
        self.pending_results.clear()
        self.bad_lines.clear()
        if self.read(REG_CTRL) & 1:
            raise RuntimeError("Core did not stop")

    def write(self, address: int, value: int, verify: bool = True) -> None:
        reply = self.command(write_command(address, value), "w")
        if verify and (reply.address != address or reply.value != (value & 0xFFFFFFFF)):
            raise RuntimeError(f"Register {address:#04x}: wrote {value:#010x}, read back {reply.value:#010x}")

    def read(self, address: int) -> int:
        reply = self.command(read_command(address), "q")
        if reply.address != address:
            raise RuntimeError(f"Asked for register {address:#04x}, got {reply.address:#04x}")
        return reply.value

    def identify(self) -> int:
        return self.command(identify_command(), "i").value

    def run_scenario(self, scenario: Scenario, channel_count: int, sweeps: int = 1) -> List[Result]:
        """Stop, program, start, and return sweeps * 32 results beginning with satellite 1."""
        self.write(REG_CTRL, 0)
        time.sleep(0.05)
        self.serial.reset_input_buffer()
        self.buffer = b""
        self.pending_results.clear()
        for address, value in scenario_writes(scenario, channel_count):
            self.write(address, value)
        self.write(REG_CTRL, 1)
        return self.results(sweeps * SATELLITES)

    def results(self, count: int, per_result_timeout: float = 2.0) -> List[Result]:
        out = self.pending_results[:count]
        del self.pending_results[: len(out)]
        while len(out) < count:
            parsed = self._next(time.monotonic() + per_result_timeout)
            if parsed is None:
                raise TimeoutError(f"Only {len(out)} of {count} results arrived")
            if isinstance(parsed, Result):
                out.append(parsed)
        return out


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------


def git_revision(path: Path) -> str:
    try:
        revision = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain"], capture_output=True, text=True, check=True
        ).stdout.strip()
        return revision + (" (with uncommitted changes)" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def describe(result: Optional[Result]) -> str:
    if result is None:
        return "no result"
    return f"freq {result.freq_offset:+d} ({result.doppler_hz:+.0f} Hz), phase {result.phase_offset}, metric {result.metric}"


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", help="Serial port (default: the board's FTDI port)")
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--sweeps", type=int, default=2, help="Full 32-satellite sweeps per scenario")
    parser.add_argument("--repeat", type=int, default=5, help="Restarts in the repeatability check")
    parser.add_argument("--soak", type=float, default=0, help="Seconds to run continuously watching for overflow")
    parser.add_argument("--bitstream", type=Path, help="Bitstream that is loaded, to record its hash")
    parser.add_argument("--report", type=Path, help="Write a Markdown report here (a .json goes next to it)")
    args = parser.parse_args(argv)

    port = args.port or find_port()
    board = Board(port, args.baud)
    record = {
        "date": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
        "port": port,
        "scenarios": [],
    }
    failures = 0
    try:
        board.sync()
        identity = board.identify()
        if identity != ID_WORD:
            raise SystemExit(f"Unexpected identity {identity:#010x}; is the self-test bitstream loaded?")
        info = board.read(REG_INFO)
        channel_count, coarse_bins = info & 0xFF, (info >> 8) & 0xFF
        record.update(identity=f"{identity:#010x}", channels=channel_count, coarse_bins_each_side=coarse_bins)
        print(f"Board on {port}: identity {identity:#010x}, {channel_count} emulator channels, "
              f"+/-{coarse_bins} coarse bins")

        root = Path(__file__).resolve().parents[1]
        record["source"] = {
            "gps-rtl": git_revision(root),
            "gps-model": git_revision(root.parent / "gps-model"),
            "fpga-utils": git_revision(root.parent / "fpga-utils"),
        }
        if args.bitstream:
            record["bitstream"] = {"file": str(args.bitstream), "sha256": sha256(args.bitstream)}

        for scenario in hardware_scenarios():
            results = board.run_scenario(scenario, channel_count, args.sweeps)
            problems = check_order(results) + check_results(scenario, results)
            present = scenario.present()
            absent_peak = max((r.metric for r in results if r.sv not in present), default=0)
            status = "info" if scenario.informational else ("PASS" if not problems else "FAIL")
            failures += status == "FAIL"
            print(f"[{status}] {scenario.name}")
            entry = {
                "name": scenario.name, "status": status, "note": scenario.note, "problems": problems,
                "absent_peak_metric": absent_peak, "satellites": [],
            }
            for sv, channel in present.items():
                found = [r for r in results if r.sv == sv]
                for r in found:
                    print(f"         SV {sv}: {describe(r)}  "
                          f"[expected freq {channel.expected_freq_offset:+g}, phase {channel.code_phase}]")
                entry["satellites"].append({
                    "sv": sv, "expected_freq_offset": channel.expected_freq_offset,
                    "expected_phase": channel.code_phase, "amplitude": channel.amplitude,
                    "results": [vars(r) for r in found],
                })
            print(f"         strongest absent satellite metric: {absent_peak}")
            for problem in problems:
                print(f"         {'note' if scenario.informational else 'PROBLEM'}: {problem}")
            record["scenarios"].append(entry)

        # Repeatability: the same signal after independent restarts. The serial
        # and system clocks are asynchronous, so the capture window can start a
        # sample earlier or later from one restart to the next and the reported
        # phase can move with it; every restart must still be within tolerance.
        scenario = Scenario("repeatability: SV 19 after restarts", [model.Channel(19, 2500, fine(-40))])
        repeats = []
        for _ in range(args.repeat):
            results = board.run_scenario(scenario, channel_count, 1)
            repeats.append(next(r for r in results if r.sv == 19))
        distinct = {(r.freq_offset, r.phase_offset) for r in repeats}
        problems = [p for r in repeats for p in check_results(scenario, [r])]
        status = "PASS" if not problems else "FAIL"
        failures += status == "FAIL"
        print(f"[{status}] {scenario.name}: {args.repeat} restarts -> {sorted(distinct)}")
        for problem in problems:
            print(f"         PROBLEM: {problem}")
        record["repeatability"] = {
            "status": status, "restarts": args.repeat, "problems": problems,
            "results": [vars(r) for r in repeats],
        }

        if args.soak > 0:
            scenario = hardware_scenarios()[0]
            board.run_scenario(scenario, channel_count, 1)
            deadline = time.monotonic() + args.soak
            count, bad, overflow = 0, 0, False
            phase_errors: Dict[int, int] = {}
            metrics: List[int] = []
            channel = scenario.channels[0]
            half = model.PERIOD // 2
            while time.monotonic() < deadline:
                batch = board.results(SATELLITES)
                count += len(batch)
                overflow |= any(r.overflow for r in batch)
                bad += bool(check_results(scenario, batch))
                for r in batch:
                    if r.sv == channel.sv:
                        error = (r.phase_offset - channel.code_phase + half) % model.PERIOD - half
                        phase_errors[error] = phase_errors.get(error, 0) + 1
                        metrics.append(r.metric)
            # Read before stopping: lowering run clears the flag and the counter.
            status_word = board.read(REG_STATUS)
            overflow |= bool(status_word & 1)
            status = "PASS" if not overflow and not bad else "FAIL"
            failures += status == "FAIL"
            histogram = {str(k): phase_errors[k] for k in sorted(phase_errors)}
            median = sorted(metrics)[len(metrics) // 2]
            print(f"[{status}] soak: {count} results in {args.soak:g} s, {bad} bad sweeps, "
                  f"overflow {'SET' if overflow else 'clear'}")
            print(f"         SV {channel.sv} phase error histogram (samples: count): {histogram}")
            print(f"         SV {channel.sv} metric: min {min(metrics)}, median {median}")
            record["soak"] = {
                "status": status, "seconds": args.soak, "results": count, "bad_sweeps": bad, "overflow": overflow,
                "phase_error_histogram": histogram, "metric_min": min(metrics), "metric_median": median,
            }

        board.write(REG_CTRL, 0)
        record["garbled_lines"] = board.bad_lines
        if board.bad_lines:
            failures += 1
            print(f"[FAIL] {len(board.bad_lines)} unreadable lines from the board: {board.bad_lines[:3]}")
    finally:
        board.close()

    record["failures"] = failures
    print(f"\n{'ALL CHECKS PASSED' if not failures else str(failures) + ' CHECK(S) FAILED'}")
    if args.report:
        write_report(args.report, record)
        print(f"Report: {args.report}")
    return 1 if failures else 0


def write_report(path: Path, record: dict) -> None:
    path.with_suffix(".json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    lines = [
        "# GpsSelfTest board run",
        "",
        f"- Date: {record['date']}",
        f"- Port: {record['port']}, identity {record.get('identity')}, "
        f"+/-{record.get('coarse_bins_each_side')} coarse bins, {record.get('channels')} emulator channels",
    ]
    for name, revision in record.get("source", {}).items():
        lines.append(f"- {name}: `{revision}`")
    if "bitstream" in record:
        lines.append(f"- Bitstream: `{record['bitstream']['file']}`, SHA-256 `{record['bitstream']['sha256']}`")
    lines += [
        "",
        f"Result: **{'all checks passed' if not record['failures'] else str(record['failures']) + ' check(s) failed'}**",
        "",
        "| Scenario | Status | Satellite | Expected freq / phase | Reported freq / phase / metric | Strongest absent |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for entry in record["scenarios"]:
        if not entry["satellites"]:
            lines.append(f"| {entry['name']} | {entry['status']} | none | | | {entry['absent_peak_metric']} |")
        for satellite in entry["satellites"]:
            reported = "; ".join(
                f"{r['freq_offset']:+d} / {r['phase_offset']} / {r['metric']}" for r in satellite["results"]
            )
            lines.append(
                f"| {entry['name']} | {entry['status']} | {satellite['sv']} | "
                f"{satellite['expected_freq_offset']:+g} / {satellite['expected_phase']} | {reported} | "
                f"{entry['absent_peak_metric']} |"
            )
    problems = [(e["name"], p) for e in record["scenarios"] for p in e["problems"]]
    if problems:
        lines += ["", "## Notes and problems", ""]
        lines += [f"- {name}: {problem}" for name, problem in problems]
    if "repeatability" in record:
        r = record["repeatability"]
        values = sorted({(x["freq_offset"], x["phase_offset"]) for x in r["results"]})
        lines += ["", f"Repeatability ({r['restarts']} restarts): {r['status']}, freq/phase values seen: {values}"]
    if "soak" in record:
        s = record["soak"]
        lines += [
            "",
            f"Soak: {s['status']}, {s['results']} results in {s['seconds']:g} s, {s['bad_sweeps']} bad sweeps, "
            f"sample overflow {'set' if s['overflow'] else 'clear'}. Phase error histogram "
            f"(samples: count) {s['phase_error_histogram']}; metric min {s['metric_min']}, "
            f"median {s['metric_median']}.",
        ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
