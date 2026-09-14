# GpsTop: acquisition core and integration contract

`GpsTop` joins the MAX2769 serial receiver to the acquisition engine and
exports results on a stream. It is board-neutral: no pin constraints, no MAX
configuration, no host transport. Tracking, navigation decoding and a position
solution do not exist in gateware yet. A passing simulation of this core is not
a receiver and not a board qualification.

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
- The serial-domain reset release is asynchronous. A board design has to
  sequence source start-up against it and check reset synchronization against
  real MAX timing; the bench's orderly reset does not cover that.

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
it. Mid-range phases come out within one sample of the fixture.

## The live boundary is lossy

The RF source cannot pause, so `GpsTop` drains and discards serial FIFO
samples between acquisition windows; the next search then cannot inherit a
stale prefix. Keeping old samples across a computation stall mixes epochs in
the next window; before the fix, the serial bench saw the timestamp jump from
632 to 952 at the ninth sample of the second window.

Inside a window the core retains samples across downstream stalls.
`capture_active` is derived from registered FFT gate, config and select state,
not from ready or valid (gating valid with ready would create a combinational
loop), and it covers fine PRN alignment through the final decimated input. The
paced tests check consecutive coarse timestamps and at least 32,768 samples in
each of two aligned fine windows: without stalls the counts are 32,768 each,
with stalls 32,769 and 32,768, the extra sample being one input accepted while
the decimator finishes its last output. This is still a windowed acquisition
stream, not a continuous transport; a tracking path will need its own sample
stream.

`sample_overflow` is sticky until reset and synchronized into the system
domain. It flags a serial FIFO write that was refused. It stays zero in the
paced bench; a separate forced-back-pressure test checks assert, hold and
clear. It does not count the intentional between-window discards.

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

## Stall capacity and fault handling

The MAX serial interface emits bursts of 16 samples into an eight-entry FIFO.
How long a downstream stall can be tolerated depends on where in the burst it
lands, on FIFO occupancy and on clock-domain synchronization; an average
sample-rate figure is not a guaranteed budget. The 50 MHz system, 61 ns
serial-clock fixture passes FFT-input pauses of four system cycles in every
64, FFT-output pauses of 100 cycles in every 1,124, and a 1,000-cycle hold on
the first result, with coarse and fine continuity, the satellite 2 frequency
and phase, and a stable result payload asserted. Those are specific bounded
schedules, not a proof for arbitrary stalls, and no tighter serial clock has
been qualified.

The long-stall case fills the FIFO, checks that `sample_overflow` asserts and
sticks, resets the core, and then acquires satellite 1 at frequency bin 0 and
phase 37 with no further overflow. Once `sample_overflow` asserts, discard
results and reset before trusting new ones. The flag is a separate port: it
neither suppresses results nor travels in the result payload, so the host must
watch it. Do not enlarge the buffering without measuring the real core's stall
pattern.

The vendor C model verifies arithmetic; the pause generators exercise stream
back-pressure, not a cycle-accurate model of the FFT IP. Qualify FFT latency
and ready behaviour, serial timing and reset release on the chosen board before
a hardware demonstration.

The Ethernet bench uses the dependency's `UdpStream(sim=true)` generic MAC and
a shorter reset timer through a separate `EthernetTestbenchSim` generator; the
board generator and its file name are unchanged. It checks register writes and
command-ID readback, LED effects, frame CRC, sample transport and a known
acquisition-result packet. It is a protocol check, not vendor I/O timing.
Initialize `verilog-ethernet` recursively before running it.

## Host tools

The UDP stream carries a flags byte before incoming payloads and after outgoing
ones; bit 0 marks the last fragment, including payloads that are exactly 507
bytes. `AxilInterface.read` waits one second by default and raises
`TimeoutError` with the address and command ID; pass `timeout=` to change it.
Run the host checks with `python -m unittest discover -s scripts/tests -v`.
They use loopback UDP and never touch lab hardware.

## Before a board demonstration

1. Identify the MAX and FPGA board revisions, the clock, and the reset and
   first-plane timing; configure the MAX; choose a host transport; write pin
   and clock constraints.
2. Synthesize, implement and close timing on the chosen board.
3. Replay an agreed capture and record the source and bitstream hashes, the
   acquisition metrics and the overflow flag with the result.

None of that can be inferred from passing cocotb tests.
