package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

/* Shifts input sample to use full dynamic range of output width.
 *
 * Ex:
 * Input is (0b1)
 */

case class ShiftGain(in_width: Int, out_width: Int) extends Component {
  assert(in_width > out_width)

  val io = new Bundle {
    val input = slave Stream (Complex(in_width))
    val output = master Stream (Complex(out_width))
  }

  val sample = Reg(Complex(in_width))

  io.input.ready := False
  io.output.valid := False
  io.output.payload.re := sample.re(in_width - out_width, out_width bits)
  io.output.payload.im := sample.im(in_width - out_width, out_width bits)

  val fsm = new StateMachine {
    val init: State = new State with EntryPoint {
      whenIsActive {
        io.input.ready := True

        when(io.input.fire) {
          sample := io.input.payload
          goto(shift)
        }
      }
    }

    val shift: State = new State {
      // True if most significant non sign bit has data
      val re_msb = sample.re.sign ^ sample.re(in_width - 2)
      val im_msb = sample.im.sign ^ sample.im(in_width - 2)

      whenIsActive {
        when((re_msb === True) || (im_msb === True)) {
          io.output.valid := True

          when(io.output.fire) {
            goto(init)
          }
        } otherwise {
          // Left shift preserving sign
          sample.re := (sample.re.sign ## sample.re(0, in_width - 2 bits) ## sample.re(0)).asSInt
          sample.im := (sample.im.sign ## sample.im(0, in_width - 2 bits) ## sample.im(0)).asSInt
        }
      }
    }
  }
}

object ShiftGainVerilog extends App {
  Config.spinal.generateVerilog(ShiftGain(16, 8))
}
