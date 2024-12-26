package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

/* Alignment math:
 *
 * Incrementing PRN decreases offset.
 * Incrementing IQ samples increases offset.
 * IQ samples must increment one every `rate` cycles to keep up with input.
 *
 * Time to align by running PRN: t = offset * rate/(rate - 1)
 * Time to align by running IQ: t = (4096 - offset)*rate
 *
 * Threshold: offset = 4096 * (rate - 1) / rate
 *
 * At 50 MHz clock and 4.092 Msps, rate = 12, threshold ~= 3755
 */

case class RemovePrn(
    iqInWidth: Int,
    iqOutWidth: Int,
    period: Int,
    phaseWidth: Int,
    sampleRate: HertzNumber,
    debug: Boolean = false,
    earlyLate: Boolean = false,
    earlyLateShift: Int = 1 // In samples
) extends Component {

  val current_freq = ClockDomain.current.frequency.getValue

  val clocks_per_sample = (current_freq / sampleRate)
  val threshold = period - ((1 << phaseWidth) * (clocks_per_sample - 1) / clocks_per_sample).toInt

  val io = new Bundle {
    val input = slave Stream (ComplexTimestamp(iqInWidth, period))

    val output_multi = master Stream (Vec(Complex(iqOutWidth), 3))
    val output_single = master Stream(Complex(iqOutWidth))

    val set = in Bool ()
    val sv = in UInt (6 bits)
    val phase_offset = in UInt (phaseWidth bits)
    val dropped = out UInt (16 bits)
  }

  // Wrap phase at period instead of integer overflow
  def wrap_phase(phase: UInt): UInt = {
    val wrapped_phase = UInt(phaseWidth bits)
    when(phase >= period) {
      wrapped_phase := (phase - period).resized
    } otherwise {
      wrapped_phase := phase.resized
    }
    wrapped_phase
  }

  val absolute_offset = Reg(UInt(phaseWidth bits)) init 0

  val prn = Prn()
  prn.io.sv := io.sv
  prn.io.set := io.set
  prn.io.inc := U"17'h4000"

  val prn_phase_history = History(prn.io.sample_count, earlyLateShift * 2 + 2, prn.io.code.fire)
  val last_prn_phase = UInt()

  if (earlyLate) {
    last_prn_phase := prn_phase_history(earlyLateShift + 2)
  } else {
    last_prn_phase := prn_phase_history(1)
  }
  val last_iq_phase = RegNextWhen(io.input.t, io.input.fire)

  // Intermediate signed value to properly handle overflows
  val offset_wide = (last_prn_phase.resize(phaseWidth + 1 bits) -
    last_iq_phase.resize(phaseWidth + 1 bits) -
    absolute_offset.resize(phaseWidth + 1 bits)).asSInt
  val offset = UInt(phaseWidth bits)

  when(offset_wide < 0) {
    offset := (offset_wide + period).asUInt.resized
  } otherwise {
    offset := offset_wide.asUInt.resized
  }

  // Figure out next offset value
  val offset_next = UInt(phaseWidth bits)

  when(io.input.fire & prn.io.code.fire) {
    offset_next := offset
  } elsewhen (prn.io.code.fire) {
    when(offset === period - 1) {
      offset_next := 0
    } otherwise {
      offset_next := offset + 1
    }
  } elsewhen (io.input.fire) {
    when(offset === 0) {
      offset_next := period - 1
    } otherwise {
      offset_next := offset - 1
    }
  } otherwise {
    offset_next := offset
  }

  // Advance PRN if it will get to alignment faster
  val throw_prn = Reg(Bool()) init False
  val throw_iq = Reg(Bool()) init False
  val aligned = Bool()
  aligned := False

  val mixerWidth = iqInWidth * 2

  val prn_code = prn.io.code
    .throwWhen(throw_prn)
    .translateInto(Stream(Fragment(Complex(mixerWidth))))((to, from) => {
      // Scale PRN to +-1 (127/-128) and zero imaginary component
      // XOR to convert False to 0x80 (-128) and True to 0x7F (127)
      when(from) {
        to.re := (1 << mixerWidth - 1) - 1
      } otherwise {
        to.re := -((1 << mixerWidth - 1) - 1)
      }

      to.im := 0
      to.last := False
    })

  val input_stream = io.input
    .throwWhen(throw_iq) // Don't send to mixer before alignment
    .translateInto(Stream(Fragment(Complex(mixerWidth))))((to, from) => {
      to.fragment.re := from.c.re @@ (U"1'b1" << (mixerWidth - iqInWidth - 1))
      to.fragment.im := from.c.im @@ (U"1'b1" << (mixerWidth - iqInWidth - 1))
      to.last := False // Don't care
    })

  val dropped = Counter(16 bits, io.input.fire && throw_iq)
  io.dropped := dropped

  def process_output(stream: Stream[Fragment[Complex]]): Stream[Complex] = {
    stream
      .haltWhen(!aligned)
      .translateInto(Stream(Complex(iqOutWidth)))((to, from) => {
        // Shift to use full scale of output
        val shift = iqOutWidth - mixerWidth + 1

        if (shift > 0) {
          to.re := (from.re << shift).resized
          to.im := (from.im << shift).resized
        } else {
          to.re := (from.re >> -shift).resized
          to.im := (from.im >> -shift).resized
        }
      })
  }

  val early_late_area = earlyLate generate new Area {
    val mixer_early = Mixer(mixerWidth)
    val mixer_prompt = Mixer(mixerWidth)
    val mixer_late = Mixer(mixerWidth)

    val inputs = StreamFork(input_stream, 3, true)

    mixer_early.io.input_a </< inputs(0)
    mixer_prompt.io.input_a </< inputs(1)
    mixer_late.io.input_a </< inputs(2)

    val prn_code_history = History(prn_code, 2 * earlyLateShift + 1, prn_code.fire, prn_code.clone.getZero)
    val prn_forked = StreamFork(prn_code, 3, true)

    mixer_early.io.input_b </< prn_forked(0).translateWith(prn_code_history(2))
    mixer_prompt.io.input_b </< prn_forked(1).translateWith(prn_code_history(earlyLateShift))
    mixer_late.io.input_b </< prn_forked(2).translateWith(prn_code_history(2 * earlyLateShift))

    val joined = StreamJoin.vec(
      Vec(
        process_output(mixer_early.io.output),
        process_output(mixer_prompt.io.output),
        process_output(mixer_late.io.output)
      )
    )

    io.output_multi << joined
    io.output_single.setIdle()
  }

  val single_output = !earlyLate generate new Area {
    val mixer = Mixer(mixerWidth)

    mixer.io.input_a << input_stream
    mixer.io.input_b << prn_code

    io.output_single << process_output(mixer.io.output)
    io.output_multi.setIdle()
  }

  val fsm = new StateMachine {
    always {
      when(io.set) {
        absolute_offset := io.phase_offset

        goto(prime_prn)
      }
    }

    // Discard PRN samples to prime PRN code history
    val prime_prn: State = new State with EntryPoint {
      val primer_counter = Counter(earlyLateShift * 2 + 1)

      onEntry {
        primer_counter.clear()
      }

      whenIsActive {
        throw_prn := True

        primer_counter.increment()

        when(primer_counter.willOverflow) {
          goto(prime)
        }
      }
    }

    // Discard first sample to get fresh data
    val prime: State = new State {
      onEntry {
        throw_iq := True
        throw_prn := True
      }

      whenIsActive {
        when(io.input.fire) {
          throw_iq := False
        }

        when(prn.io.code.fire) {
          throw_prn := False
        }

        when(!throw_iq & !throw_prn) {
          goto(idle)
        }
      }
    }

    val idle: State = new State {
      whenIsActive {
        // In sims, IQ samples aren't limited by sample rate
        if (debug) {
          when(offset > period / 2) {
            goto(advance_prn)
          } otherwise {
            goto(advance_iq)
          }
        } else {
          when(offset > threshold) {
            goto(advance_prn)
          } otherwise {
            goto(advance_iq)
          }
        }
      }
    }

    val advance_prn: State = new State {
      whenIsActive {
        if (!debug) {
          throw_iq := True
        }
        throw_prn := True

        when(offset_next === 0) {
          throw_prn := False
          throw_iq := False
          goto(locked)
        }
      }
    }

    val advance_iq: State = new State {
      whenIsActive {
        throw_iq := True

        when(offset_next === 0) {
          throw_iq := False
          goto(locked)
        }
      }
    }

    val locked: State = new State {
      whenIsActive {
        aligned := True
      }
    }
  }
}

object RemovePrnVerilog extends App {
  Config.spinal.generateVerilog(RemovePrn(2, 8, 4092, 12, 4.092 MHz))
}
