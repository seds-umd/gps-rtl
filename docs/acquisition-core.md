# GpsTop: acquisition core and integration contract

`GpsTop` joins the MAX2769 serial receiver to the acquisition engine and
exports results on a stream. It is board-neutral: no pin constraints, no MAX
configuration, no host transport. Tracking, navigation decoding and a position
solution do not exist in gateware yet.

## Clocks, reset and input format

- System clock and reset come from `Config.scala` (50 MHz in the current
  design). The PRN alignment path derives a threshold from the declared
  frequency, so change both together.
- The serial side has its own clock. Samples arrive in blocks of 16 as four
  16-bit planes in the order I-MSB, I-LSB, Q-MSB, Q-LSB; `data_sync` marks the
  first bit of each plane. After reset the first plane must be I-MSB; starting
  mid-block is not supported.
- Signed 2-bit I/Q and a sample counter modulo 4092 cross into the system
  domain through the existing asynchronous FIFO.
- `time_sync` is unused. It is not a PPS or GPS-time input.
- The serial-domain reset release is asynchronous; a board design has to
  sequence source start-up against it.

The default search spans 24 coarse frequency bins on each side and elaborates
as `GpsTopVerilog`. The regression uses `GpsTopSimVerilog`, a two-bin span, to
keep run time bounded; it keeps `debug=false` so the real-time alignment path
is exercised.

## Results

| Field | Type | Meaning |
| --- | --- | --- |
| `sv` | unsigned 6 bits | Satellite PRN, 1 to 32 |
| `freq_offset` | signed 12 bits | Frequency in units of 4.092e6 / (4096 * 8) Hz |
| `phase_offset` | unsigned 12 bits | C/A code phase relative to the 4092-sample timestamp epoch |
| `snr` | unsigned 8 bits | Saturated detection metric; not a calibrated dB value |

A result transfers on `valid && ready`. While the consumer stalls, the result
stays pending and acquisition does not start the next satellite. Consume
low-metric results too and filter them downstream. The metric cutoff of 8 used
by older code is not calibrated: in the serial bench an absent satellite
produced 10 and the present one produced 255.

Phase arithmetic: the FFT bin is mapped from the 4096-point domain to 4092
samples first, then the timestamp origin is subtracted modulo 4092. The reverse
order gives timestamp-dependent errors; the shifted-origin regression covers
it. In simulation, where each search starts at the same point in the signal,
phases come out within one sample of the fixture.

On a board the capture window starts wherever the signal happens to be, and
`phase_offset` is only good to two samples (half a chip). The FFT is 4096
points but a C/A code period is 4092 samples, so the circular correlation sees
the code wrap four samples early: there are two peaks four samples apart,
weighted by where the code boundary falls in the window. When it falls near
the middle they merge into a flat top five samples wide at half height, and
`scale4096_4092` can land anywhere on it. Measured on an Arty S7-25 over 392
acquisitions of one satellite, the error ranged from -2 to +2 samples (see
`status-2026-11.md`). The same effect costs up
to 6 dB of coarse sensitivity. A two-sample error then puts the fine stage
half a chip off, which halves its correlation (about 6 dB in theory; on the
board the saturating metric fell from 255 to about 135 on a clean signal,
which fits but does not measure it). A tracking loop will pull in half a chip.
Anything that needs better from acquisition alone has to make one code period
span the FFT exactly: resample the signal and the replica to 4096 points per
period and convert the phase back, or correlate over a true 4092-sample
period. Padding the frame with repeated samples at the end is what happens
now and does not help. Neither option has been tried.

## The live boundary

The RF source cannot pause, so `GpsTop` drains and discards serial FIFO
samples between acquisition windows; the next search then cannot inherit a
stale prefix. Before this was fixed, the serial bench saw the timestamp jump
from 632 to 952 at the ninth sample of the second window.

Inside a window the core retains samples across downstream stalls.
`capture_active` is derived from registered FFT gate, config and select state,
not from ready or valid (gating valid with ready would create a combinational
loop), and it covers fine PRN alignment through the final decimated input. The
paced tests check consecutive coarse timestamps and at least 32,768 samples in
each of two aligned fine windows: without stalls the counts are 32,768 each,
with stalls 32,769 and 32,768, the extra sample being one input accepted while
the decimator finishes its last output.

`sample_overflow` is sticky until reset and synchronized into the system
domain. It flags a serial FIFO write that was refused; it does not count the
intentional between-window discards. It is a separate port, not part of the
result payload, so the host has to watch it. Once it asserts, discard results
and reset before trusting new ones.

### Stall budget

The MAX serial interface emits bursts of 16 samples into an eight-entry FIFO,
so how long a downstream stall can be tolerated depends on where in the burst
it lands and on FIFO occupancy. With a 50 MHz system clock and a 61 ns serial
clock, the bench passes FFT-input pauses of four system cycles in every 64,
FFT-output pauses of 100 cycles in every 1,124, and a 1,000-cycle hold on the
first result, with coarse and fine continuity and the satellite 2 result
asserted throughout. The long-stall case fills the FIFO, checks that
`sample_overflow` asserts and sticks, resets the core, and then acquires
satellite 1 at frequency bin 0 and phase 37 with no further overflow.

## Generators and benches

```bash
sbt "runMain gps.GpsTopVerilog"       # hardware parameters -> hw/gen/GpsTop.v
sbt "runMain gps.GpsTopSimVerilog"    # two-bin span        -> hw/gen/GpsTopSim.v
make TESTS=GpsTop                     # needs the Linux x86_64 FFT C model
make TESTS=EthernetTestbench          # same model plus generic GMII
```

The serial bench generates a satellite 2 signal, serializes it as MAX bit
planes without injected timestamps, and checks the first two results: the
satellite 2 metric must be more than four times the satellite 1 metric, and
frequency and phase must match the fixture (bin 8; phase 36 for an expected
37). The second search starts at an arbitrary serial timestamp. A second case
repeats this under FFT input and output pauses and a held result; a third
forces an overflow, resets the core and acquires a fresh satellite 1 fixture.

The Ethernet bench uses the dependency's `UdpStream(sim=true)` generic MAC and
a shorter reset timer through a separate `EthernetTestbenchSim` generator; the
board generator and its file name are unchanged. It checks register writes and
command-ID readback, LED effects, frame CRC, sample transport and a known
acquisition-result packet. Initialize `verilog-ethernet` recursively before
running it.

## Host tools

The UDP stream carries a flags byte before incoming payloads and after outgoing
ones; bit 0 marks the last fragment, including payloads that are exactly 507
bytes. `AxilInterface.read` waits one second by default and raises
`TimeoutError` with the address and command ID; pass `timeout=` to change it.
Run the host checks with `python -m unittest discover -s scripts/tests -v`.
They use loopback UDP and never touch lab hardware.

## Code removal alignment

`RemovePrn` lines the local PRN up with the incoming samples using
offset = (PRN phase - sample timestamp - phase_offset) modulo 4092. That
difference reaches -8182, so it is taken one term at a time with a wrap after
each. Until November 2026 it was a single 13-bit subtraction with one wrap,
which overflowed whenever phase_offset + timestamp exceeded PRN phase + 4092
and locked the PRN eight samples (two chips) early: the coarse result was right,
the fine stage then found nothing and the metric collapsed to the noise level.
With arbitrary code phases that is roughly half of all acquisitions. It went
unseen because the only bench that used the real-time alignment path
(`debug = false`) did so at a phase of 37. `RemovePrn`'s own bench now covers
late phases, and the board self-test sweeps the phase across the whole period.

## What the simulation does not cover

- The Xilinx FFT C model checks arithmetic only. The pause generators exercise
  stream back-pressure, not the real IP's cycle-accurate ready and latency
  behaviour. Measure those on the chosen board before trusting the stall budget.
- Only the 50 MHz / 61 ns clock pairing has been run. A tighter serial clock
  changes the budget.
- Reset synchronization against real MAX timing, pin constraints, timing
  closure and a host transport are all board work that has not been done.
- This is a windowed acquisition stream, not a continuous transport. A tracking
  path will need its own sample stream.

## What the board self-test adds

`GpsSelfTest` (see the README) runs `GpsTop` on an Arty S7 against the real
FFT core, with an on-chip MAX2769 emulator on a separate 16.368 MHz clock. It
covers the first two points above for that clock pairing: the design meets
timing at 50 MHz on a Spartan-7, and in a five-minute continuous run with the
vendor core's real latency and back-pressure `sample_overflow` never asserted.
It does not cover a real MAX2769 (pin timing, reset sequencing against a clock
that is already running, SPI configuration), live-sky signals or a host
transport other than the test UART.

## Before a board demonstration

1. Identify the MAX and FPGA board revisions, the clock, and the reset and
   first-plane timing; configure the MAX; choose a host transport; write pin
   and clock constraints.
2. Synthesize, implement and close timing on the chosen board.
3. Replay an agreed capture and record the source and bitstream hashes, the
   acquisition metrics and the overflow flag with the result.
