# GPS acquisition core and integration contract

`GpsTop` is a board-neutral component joining the existing MAX serial receiver
to acquisition. It exports results to a caller-provided stream consumer. It is
not a complete GPS receiver or a board bitstream: tracking, navigation decoding,
position calculation, MAX configuration, pin constraints and a host transport
are separate integration work.

## Inputs and clocking

The core uses the system clock/reset configured in `Config.scala` (50 MHz for
the current design) and a separate serial clock. The serial bench sends blocks
of 16 samples as four 16-bit planes: I-MSB, I-LSB, Q-MSB, Q-LSB. `data_sync`
marks the first bit of each plane. Signed two-bit I/Q and a sample counter
modulo 4092 pass through the existing asynchronous FIFO to acquisition.

The `time_sync` input is currently unused. It is not a PPS or GPS-time service.
After reset, the first plane must be I-MSB. Starting midway through a block is
not supported. The current serial-domain reset release is asynchronous; a board
implementation must coordinate source startup and qualify reset synchronization
against actual MAX timing. The simulation's orderly reset is not proof of this
physical behavior.

Do not change the system clock without updating its declared frequency: the
real-time PRN alignment path derives a threshold from it. The default acquisition
search spans 24 coarse bins on either side; the separate simulation generator
uses 2 to keep regression time bounded. It keeps `debug=false`, exercising the
real-time alignment path rather than the unpaced acquisition bench's shortcut.
The default 24-bin span is elaborated, but the full system regression exercises
only the narrower simulation span.

## Results

| Field | Type | Meaning |
| --- | --- | --- |
| `sv` | unsigned 6 bits | Satellite PRN identifier, 1–32 |
| `freq_offset` | signed 12 bits | Frequency in units of `4.092e6 / (4096 * 8)` Hz |
| `phase_offset` | unsigned 12 bits | C/A phase relative to the 4092-sample input timestamp epoch |
| `snr` | unsigned 8 bits | Saturated acquisition detection metric, not a calibrated dB value |

A result transfers when `valid && ready`. Results remain pending while the
consumer is stalled; acquisition does not search another satellite until that
transfer. Consume low-metric results too; filtering them must not stop draining
the stream. No UART or SPI register protocol is implied by this component port.

The FFT phase is first mapped from its 4096-point domain to 4092 samples. The
timestamp origin is then subtracted modulo 4092. Reversing those operations
creates timestamp-dependent phase errors; the shifted-origin regression covers
that previously untested behavior.

The RF source cannot pause. `GpsTop` continuously drains the serial FIFO and
intentionally discards samples while acquisition is not accepting a window.
Retaining the FIFO's old samples across a long computation stall mixes epochs
in the next window: the serial regression reproduced a timestamp jump from 632
to 952 at its ninth sample. The live-input adapter prevents that stale prefix.
This boundary is deliberately lossy; it is not a buffered transport stream.
The paced regression checks consecutive timestamps inside each coarse window.

`sample_overflow` is sticky until reset and synchronized into the system clock
domain. It reports a serial FIFO write that could not be accepted. It remains
zero in the connected paced regression; a separate forced-backpressure test
checks assertion, stickiness and reset. It does not count the intentional
outside-window discards or prove continuous reception at other clock rates.
A future tracking path needs its own continuous sample stream before acquisition;
sharing acquisition's acceptance windows would discard tracking samples.

## Simulation and board generators

```bash
sbt "runMain gps.GpsTopVerilog"       # hardware parameters, generated GpsTop.v
sbt "runMain gps.GpsTopSimVerilog"    # narrow search, generated GpsTopSim.v
make TESTS=GpsTop                    # Linux x86_64 FFT model required
make TESTS=EthernetTestbench          # same arithmetic model plus generic GMII
```

The serial integration test generates a satellite 2 signal, serializes it without
injecting timestamps, and checks the first two results. The satellite 2 metric
must exceed satellite 1 by more than four times and its frequency and phase
must match the fixture. The existing metric cutoff of 8 is not a calibrated
detection threshold: the absent satellite 1 produced a metric of 10. The second search starts at an arbitrary serial timestamp. This verifies
the connected acquisition path for that fixture, not RF sensitivity, multi-SV
capacity or flight readiness.

The Ethernet simulation uses the dependency's existing `UdpStream(sim=true)`
generic MAC I/O and a shorter reset timer. The board generator still uses Xilinx
I/O and its original timer. Separate generated module/file names prevent a
simulation variant from silently replacing a board build. UDP regression checks
register commands, command-ID readback, LED effects, frame CRC, sample transport
and a known acquisition-result packet. It is a protocol/arithmetic simulation,
not vendor I/O timing verification. Initialize `verilog-ethernet` recursively.

## Host tools

The UDP stream carries a flags byte before incoming payloads and a flags byte
after outgoing payloads. Flag bit 0 marks the last fragment. Payload boundaries
at exactly 507 bytes still need that flag. `AxilInterface.read` waits up to one
second by default and raises `TimeoutError` with the address and command ID if
no reply arrives; callers can pass `timeout=` explicitly.

Run host checks with `python -m unittest discover -s scripts/tests -v` in the
activated environment. They use real loopback UDP for framing and an unanswered
read; they do not contact or operate the lab hardware.

## Physical handoff

Before a board demonstration, identify the actual MAX and FPGA board/revisions,
confirm the clock and reset/first-plane timing, configure the MAX, select a host
transport, and provide pin/clock constraints. Then run synthesis, implementation
and timing analysis and replay an agreed capture. Record the bitstream/source
hash, acquisition metrics, overflow observations and captured data with the
result. Those checks require the selected hardware/toolchain and cannot be
inferred from passing cocotb tests.

### In-window readiness limitation

The live-input boundary assumes acquisition accepts each presented sample during
an open window. The decimator's one-cycle stall fits between samples at the
bench's approximately twelve system clocks per sample. The arithmetic FFT model
does not emulate a real core's ready stalls: an in-window stall coinciding with
a sample can discard it, and `sample_overflow` does not report that loss. The
regression monitors both coarse windows and the aligned fine-input windows;
it observed 32,777 and 32,768 consecutive fine-input samples for the two PRNs. Qualify the actual FFT
ready/latency behavior and repeat continuity checks before using this adapter on
hardware; the passing fixture does not establish those properties.
