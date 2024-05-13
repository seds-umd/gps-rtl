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
  val threshold = ((1 << phaseWidth) * (clocks_per_sample - 1) / clocks_per_sample).toInt

  val io = new Bundle {
    val input = slave Stream (ComplexTimestamp(iqInWidth, period))
    val output = master Stream (Complex(iqOutWidth))

    val set = in Bool ()
    val sv = in UInt (6 bits)
    val phase_offset = in UInt (phaseWidth bits)
  }

  val prn = PRN()
  prn.io.sv := io.sv
  prn.io.set := io.set
  prn.io.inc := U"17'h4000"

  val offset = (io.input.t + 1 - prn.io.sample_count - io.phase_offset).resize(phaseWidth bits)
  // val aligned = offset === 0

  // Advance PRN if it will get to alignment faster
  // val advance_prn = offset < threshold
  val throw_prn = Bool()
  val throw_iq = Bool()
  val aligned = Bool()

  val mixer = Mixer(iqInWidth)

  mixer.io.input_a << io.input
    .throwWhen(throw_iq) // Don't send to mixer before alignment
    .translateInto(Stream(Fragment(Complex(iqInWidth))))((to, from) => {
      to.fragment := from.c
      to.last := False // Don't care
    })
    .stage()

  mixer.io.input_b << prn.io.code
    .throwWhen(throw_prn)
    .translateInto(Stream(Fragment(Complex(iqInWidth))))((to, from) => {
      // Scale PRN to +-1 (127/-128) and zero imaginary component
      // XOR to convert False to 0x80 (-128) and True to 0x7F (127)
      to.re := from.asSInt.resize(iqInWidth bits) ^ (S"1'b1" << iqInWidth - 1)
      to.im := 0
      to.last := False
    })

  io.output << mixer.io.output
    .haltWhen(!aligned)
    .translateInto(Stream(Complex(iqOutWidth)))((to, from) => {
      to.re := from.re.resized
      to.im := from.im.resized
    })

  val fsm = new StateMachine {
    always {
      when(io.set) {
        when(offset < threshold) {
          goto(advance_prn)
        } otherwise {
          goto(advance_iq)
        }
      } elsewhen (offset === 1) {
        goto(locked)
      }
    }

    throw_prn := False
    throw_iq := False
    aligned := False

    // Empty, always block handles initialization
    val idle: State = new State with EntryPoint {}

    val advance_prn: State = new State {
      whenIsActive {
        throw_prn := True
        throw_iq := True
      }
    }

    val advance_iq: State = new State {
      whenIsActive {
        throw_iq := True
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
