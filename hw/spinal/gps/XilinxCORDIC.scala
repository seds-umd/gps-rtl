package gps

import spinal.core._
import spinal.lib._

import ethernet.Utils

case class CordicBundle(data_width: Int, user_width: Int) extends Bundle {
  val data = Bits(data_width bits)
  val user = Bits(user_width bits)
}

case class XilinxCORDIC() extends BlackBox {
  val io = new Bundle {
    val aclk = in Bool ()
    val aresetn = in Bool ()

    val phase = slave Stream (new CordicBundle(16, 3))
    val dout = master Stream (new CordicBundle(32, 3))
  }

  noIoPrefix()
  mapCurrentClockDomain(io.aclk, io.aresetn, resetActiveLevel = LOW)

  private def renameIO(): Unit = {
    io.flatten.foreach(bt => {
      Utils.rename_replace(bt, "ready", "tready")
      Utils.rename_replace(bt, "valid", "tvalid")
      Utils.rename_replace(bt, "payload_", "t")
      Utils.rename_replace(bt, "phase", "s_axis_phase")
      Utils.rename_replace(bt, "dout", "m_axis_dout")
    })
  }

  addPrePopTask(() => renameIO())
}

case class CordicWrapper(phase_width: Int = 12, output_width: Int = 9, with_user: Boolean = false) extends Component {
  val actual_phase_width = phase_width - 2
  val actual_dout_width = output_width - 1

  val io = new Bundle {
    val phase = slave Stream(UInt(actual_phase_width bits))
    val dout = master Stream(Complex(actual_dout_width))
  }

  // TODO: add user signals
  // TODO: convert output into something that makes sense

  val cordic = XilinxCORDIC()

  // Input phase is 0-1023 for 12 bit input (10 bit actual)
  cordic.io.phase << io.phase.translateInto(cordic.io.phase.clone())((to, from) => {
    when(from > (1 << (actual_phase_width - 1))) {
      to.data := from.asBits.resized
    } otherwise {
      to.data := ((0x7 << actual_phase_width) + from).asBits.resized
    }
    to.user := 0
  })

  // Output is +-128 for 9 bit output (8 bit actual)
  io.dout << cordic.io.dout.translateInto(io.dout.clone())((to, from) => {
    to.re := from.data.asSInt(0, actual_dout_width+1 bits).sat(1)
    to.im := from.data.asSInt(16, actual_dout_width+1 bits).sat(1)
  })
}

// case class CordicTest() extends Component {
//   val io = new Bundle {
//     val phase = slave Stream(new CordicBundle(16, 3))
//     val dout = master Stream(new CordicBundle(32, 3))
//   }

//   val cordic = XilinxCORDIC()

//   cordic.io.s_axis_phase << io.phase
//   cordic.io.m_axis_dout >> io.dout
// }

// object CordicTestVerilog extends App {
//   Config.spinal.generateVerilog(CordicTest())
// }
