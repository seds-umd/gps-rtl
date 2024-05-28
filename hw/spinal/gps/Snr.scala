package gps

import spinal.core._
import spinal.lib.fsm._

// Based on https://projectf.io/posts/division-in-verilog/
case class Snr(width: Int = 32) extends Component {
  val io = new Bundle {
    val num = in UInt (width bits)
    val den = in UInt (width bits)
    val res = out UInt (width bits)
    val rem = out UInt (width bits)

    val start = in Bool ()
    val busy = out Bool ()
    val valid = out Bool ()
    val error = out Bool ()
  }

  io.res.setAsReg()
  io.rem.setAsReg()

  io.busy.setAsReg() init False
  io.valid.setAsReg() init False
  io.error.setAsReg() init False

  val den1 = Reg(UInt(width bits))
  val quo = Reg(UInt(width bits))
  val acc = Reg(UInt(width + 1 bits))
  val i = Reg(UInt(log2Up(width + 1) bits))

  val fsm = new StateMachine {
    always {
      when(io.start) {
        i := 0
        io.valid := False

        when(io.den === 0) {
          io.busy := False
          io.error := True
        } otherwise {
          io.busy := True
          io.error := False

          den1 := io.den
          acc := U(0, width bits) @@ io.num(width - 1)
          quo := io.num(0, width - 1 bits) @@ U(0, 1 bit)

          goto(running)
        }
      }
    }

    val idle: State = new State with EntryPoint {}

    val running: State = new State {
      whenIsActive {
        when(i === width) {
          // Done
          io.busy := False
          io.valid := True
          io.res := quo
          io.rem := acc(1, width bits)

          goto(idle)
        } otherwise {
          // Continue iteration
          i := i + 1

          when(acc >= den1) {
            acc := ((acc - den1) @@ quo @@ U"1'b1") (width, width + 1 bits)
            quo := ((acc - den1) @@ quo @@ U"1'b1") (0, width bits)
          } otherwise {
            acc := ((acc @@ quo) << 1) (width, width + 1 bits)
            quo := ((acc @@ quo) << 1) (0, width bits)
          }
        }
      }
    }

    val done: State = new State {
      whenIsActive {
        io.valid := True
        io.busy := False
        io.error := False
      }
    }
  }
}

object SnrVerilog extends App {
  Config.spinal.generateVerilog(Snr(32))
}
