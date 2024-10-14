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
