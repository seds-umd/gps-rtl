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

case class RemovePrn(input_width: Int, config: GpsConfig) extends Component {
  val clocks_per_sample = (config.f_logic / config.f_samp)

  // Threshold where it's faster to advance PRN instead of IQ
  val threshold = config.prn_period - ((1 << config.fft_bits) * (clocks_per_sample - 1) / clocks_per_sample).toInt

  val io = new Bundle {
    val input = slave Stream (ComplexTimestamp(input_width, config.prn_period))

    val output = master Stream (Vec(ComplexTimestamp(config.prn_output_width, config.prn_period), 3))

    val set = in Bool ()
    val sv = in UInt (6 bits)
    val phase_offset = in UInt (config.fft_bits bits)

    val dropped = out UInt (16 bits)

    val freq_adj = slave Flow (SInt(config.prn_counter_width - 12 bits))
  }

  // Wrap phase at period instead of integer overflow
  def wrap_phase(phase: UInt): UInt = {
    val wrapped_phase = UInt(config.fft_bits bits)
    when(phase >= config.prn_period) {
      wrapped_phase := (phase - config.prn_period).resized
    } otherwise {
      wrapped_phase := phase.resized
    }
    wrapped_phase
  }

  val prn = Prn(config.prn_counter_width)
  prn.io.ratio := 0.25
  prn.io.sv.valid := Delay(io.set, 1)
  prn.io.sv.payload := Delay(io.sv, 1)
  prn.io.freq_adj << io.freq_adj

  val set_area = new ResetArea(io.set, true) {
    // Target offset
    val offset_target = Reg(UInt(config.fft_bits bits)) init 0

    when(Delay(io.set, 1)) {
      offset_target := Delay(io.phase_offset, 1)
    }

    val prn_phase_history = History(prn.io.sample_count, 2 * config.early_late_shift + 1, prn.io.code.fire)
    val last_prn_phase = prn_phase_history(config.early_late_shift + 1)
    val last_iq_phase = RegNextWhen(io.input.t, io.input.fire)

    // Intermediate signed value to properly handle overflows
    val wide_width = config.fft_bits + 2
    val offset_signed1 = last_prn_phase.resize(wide_width bits).asSInt -
      last_iq_phase.resize(wide_width bits).asSInt -
      offset_target.resize(wide_width bits).asSInt

    // val offset_signed = (offset_signed1 < config.prn_period) ? (offset_signed1 - config.prn_period) | offset_signed1
    val offset_signed = offset_signed1

    val offset =
      ((offset_signed < 0) ? (offset_signed + config.prn_period) | offset_signed).asUInt.resize(config.fft_bits bits)

    // Determine what the next offset value will be
    val offset_next = UInt(config.fft_bits bits)

    when(io.input.fire & prn.io.code.fire) {
      // Both advance
      offset_next := offset

    } elsewhen (prn.io.code.fire) {
      // Code advances
      when(offset === config.prn_period - 1) {
        offset_next := 0
      } otherwise {
        offset_next := offset + 1
      }

    } elsewhen (io.input.fire) {
      // Input advances
      when(offset === 0) {
        offset_next := config.prn_period - 1
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

    val mixerWidth = input_width * 2

    val prn_code = prn.io.code
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
      .translateInto(Stream(Fragment(ComplexTimestamp(mixerWidth, config.prn_period))))((to, from) => {
        to.c.re := from.c.re @@ (U"1'b1" << (mixerWidth - input_width - 1))
        to.c.im := from.c.im @@ (U"1'b1" << (mixerWidth - input_width - 1))
        to.t := from.t
        to.last := False // Don't care
      })

    val dropped_iq = Counter(16 bits, io.input.fire && throw_iq)
    val dropped_prn = Counter(16 bits, prn.io.code.fire && throw_prn)
    io.dropped := dropped_iq

    def process_output(stream: Stream[Fragment[ComplexTimestamp]]): Stream[ComplexTimestamp] = {
      stream
        .stage() // Buffer output for StreamJoin to prevent deadlock
        .translateInto(Stream(ComplexTimestamp(config.prn_output_width, config.prn_period)))((to, from) => {
          // Shift to use full scale of output
          val shift = config.prn_output_width - mixerWidth + 1

          if (shift > 0) {
            to.c.re := (from.c.re << shift).resized
            to.c.im := (from.c.im << shift).resized
          } else {
            to.c.re := (from.c.re >> -shift).resized
            to.c.im := (from.c.im >> -shift).resized
          }
          to.t := from.t
        })
    }

    val mixer_early = MixerTimestamp(mixerWidth, config.prn_period)
    val mixer_prompt = MixerTimestamp(mixerWidth, config.prn_period)
    val mixer_late = MixerTimestamp(mixerWidth, config.prn_period)

    val inputs = StreamFork(input_stream, 3, false)

    mixer_early.io.input_a << inputs(0)
    mixer_prompt.io.input_a << inputs(1)
    mixer_late.io.input_a << inputs(2)

    val prn_code_history: Vec[Complex] =
      History(prn_code, 2 * config.early_late_shift + 1, prn_code.fire, prn_code.fragment.clone.getZero)
    val prn_forked = StreamFork(prn_code.throwWhen(throw_prn).haltWhen(!aligned), 3, true)

    mixer_early.io.input_b </< prn_forked(0).translateWith(prn_code_history(0)).addFragmentLast(False)
    mixer_prompt.io.input_b </< prn_forked(1)
      .translateWith(prn_code_history(config.early_late_shift))
      .addFragmentLast(False)
    mixer_late.io.input_b </< prn_forked(2)
      .translateWith(prn_code_history(2 * config.early_late_shift))
      .addFragmentLast(False)

    io.output << StreamJoin
      .vec(
        Vec(
          process_output(mixer_early.io.output),
          process_output(mixer_prompt.io.output),
          process_output(mixer_late.io.output)
        )
      )

    val fsm = new StateMachine {
      // Discard PRN samples to prime PRN code history
      val prime_prn: State = new State with EntryPoint {
        val primer_counter = Counter(prn_code_history.length)

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

          when(prn_code.fire) {
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
          // if (config.debug) {
          //   when(offset > config.prn_period / 2) {
          //     goto(advance_prn)
          //   } otherwise {
          //     goto(advance_iq)
          //   }
          // } else {
          //   when(offset > threshold) {
          //     goto(advance_prn)
          //   } otherwise {
          //     goto(advance_iq)
          //   }
          // }
          goto(advance_prn)
        }
      }

      val advance_prn: State = new State {
        whenIsActive {
          // if (!config.debug) {
          //   throw_iq := True
          // }
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
  }.setName("") // No prefix in verilog
}

object RemovePrnVerilog extends App {
  val gps_config = GpsConfig(debug = true)
  Config.spinal.generateVerilog(RemovePrn(2, gps_config))
}
