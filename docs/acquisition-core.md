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

The RF source cannot pause, so `GpsTop` drains the serial FIFO continuously and
discards samples while acquisition is not accepting a window. Keeping old
samples across a computation stall mixes epochs in the next window; before the
fix, the serial bench saw the timestamp jump from 632 to 952 at the ninth
sample of the second window. The bench now checks consecutive timestamps inside
every coarse window and every aligned fine window (32,777 and 32,768
consecutive fine samples for the two PRNs).

`sample_overflow` is sticky until reset and synchronized into the system
domain. It flags a serial FIFO write that was refused. It stays zero in the
paced bench; a separate forced-back-pressure test checks assert, hold and
clear. It does not count the intentional between-window discards.

Known gap: inside a window the core is assumed to accept every sample on
arrival. The decimator stalls `ready` for one cycle every eight samples. At the
bench ratio of about twelve system clocks per sample that never coincides with
an arrival, but at a tighter ratio, or with a real FFT core that back-pressures
during load, a coinciding stall silently drops the sample and the fine-window
PRN alignment is lost for the rest of that window. `sample_overflow` does not
report this. Qualify the real FFT core's ready behaviour and repeat the
continuity checks at the target clock ratio before using this boundary on
hardware. A tracking path will need its own continuous sample stream; it cannot
share acquisition's windows.

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
37). The second search starts at an arbitrary serial timestamp.

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
