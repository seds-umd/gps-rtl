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

case class RemovePrn(iqInWidth: Int, iqOutWidth: Int, period: Int, phaseWidth: Int, sampleRate: HertzNumber)
    extends Component {

  val current_freq = ClockDomain.current.frequency.getValue

  val clocks_per_sample = (current_freq / sampleRate)
  val threshold = period - ((1 << phaseWidth) * (clocks_per_sample - 1) / clocks_per_sample).toInt

  val io = new Bundle {
    val input = slave Stream (ComplexTimestamp(iqInWidth, period))
    val output = master Stream (Complex(iqOutWidth))

    val set = in Bool ()
    val sv = in UInt (6 bits)
    val phase_offset = in UInt (phaseWidth bits)
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

  val absolute_offset = Reg(UInt(phaseWidth bits))

  val prn = PRN()
  prn.io.sv := io.sv
  prn.io.set := io.set
  prn.io.inc := U"17'h4000"

  val last_iq_phase = RegNextWhen(io.input.t, io.input.fire)
  val last_prn_phase = RegNextWhen(prn.io.sample_count, prn.io.code.fire)

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
  val throw_prn = Reg(Bool())
  val throw_iq = Reg(Bool())
  val aligned = Bool()

  val mixerWidth = iqInWidth * 2
  val mixer = Mixer(mixerWidth)

  mixer.io.input_a << io.input
    .throwWhen(throw_iq) // Don't send to mixer before alignment
    .translateInto(Stream(Fragment(Complex(mixerWidth))))((to, from) => {
      to.fragment.re := from.c.re @@ (U"1'b1" << (mixerWidth - iqInWidth - 1))
      to.fragment.im := from.c.im @@ (U"1'b1" << (mixerWidth - iqInWidth - 1))
      to.last := False // Don't care
    })

  mixer.io.input_b << prn.io.code
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

  io.output << mixer.io.output
    .haltWhen(!aligned)
    .translateInto(Stream(Complex(iqOutWidth)))((to, from) => {
      // Shift to use full scale of output
      to.re := (from.re << (iqOutWidth - mixerWidth + 1)).resized
      to.im := (from.im << (iqOutWidth - mixerWidth + 1)).resized
    })

  val fsm = new StateMachine {
    always {
      when(io.set) {
        absolute_offset := io.phase_offset

        goto(prime)
      }
    }

    aligned := False

    // Discard first sample to get fresh data
    val prime: State = new State with EntryPoint {
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
        when(offset > threshold) {
          goto(advance_prn)
        } otherwise {
          goto(advance_iq)
        }
      }
    }

    val advance_prn: State = new State {
      whenIsActive {
        throw_prn := True
        throw_iq := True

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

case class RemovePrnWrapper(iqInWidth: Int, iqOutWidth: Int, period: Int, phaseWidth: Int, sampleRate: HertzNumber)
    extends Component {
  val io = new Bundle {
    val input = slave Stream (ComplexTimestamp(iqInWidth, period).asBits)
    val output = master Stream (Complex(iqOutWidth).asBits)

    val set = in Bool ()
    val sv = in UInt (6 bits)
    val phase_offset = in UInt (phaseWidth bits)
  }

  val dut = RemovePrn(iqInWidth, iqOutWidth, period, phaseWidth, sampleRate)

  dut.io.input << io.input.translateInto(Stream(ComplexTimestamp(iqInWidth, period)))((to, from) => {
    to.assignFromBits(from)
  })

  io.output << dut.io.output.translateInto(Stream(Complex(iqOutWidth).asBits))((to, from) => {
    to := from.asBits
  })

  dut.io.set <> io.set
  dut.io.sv <> io.sv
  dut.io.phase_offset <> io.phase_offset
}

object RemovePrnVerilog extends App {
  Config.spinal.generateVerilog(RemovePrnWrapper(2, 8, 4092, 12, 4.092 MHz))
}
