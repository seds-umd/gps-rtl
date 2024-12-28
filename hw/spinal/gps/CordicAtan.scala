package gps

import spinal.core._
import spinal.lib._

import ethernet.Utils

case class CordicAtan() extends BlackBox {
  val io = new Bundle {
    val aclk = in Bool ()
    val aresetn = in Bool ()

    val xy = slave Stream (new CordicBundle(32, 3))
    val dout = master Stream (new CordicBundle(16, 3))
  }

  noIoPrefix()
  mapCurrentClockDomain(io.aclk, io.aresetn, resetActiveLevel = LOW)

  private def renameIO(): Unit = {
    io.flatten.foreach(bt => {
      Utils.rename_replace(bt, "ready", "tready")
      Utils.rename_replace(bt, "valid", "tvalid")
      Utils.rename_replace(bt, "payload_", "t")
      Utils.rename_replace(bt, "xy", "s_axis_cartesian")
      Utils.rename_replace(bt, "dout", "m_axis_dout")
    })
  }

  addPrePopTask(() => renameIO())
}

case class CordicAtanWrapper(cartesian_width: Int = 12, output_width: Int = 11, with_user: Boolean = false)
    extends Component {
  val actual_cartesian_width = cartesian_width - 1
  val actual_output_width = output_width - 2

  val io = new Bundle {
    val cartesian = slave Stream (Complex(actual_cartesian_width))
    val dout = master Stream (SInt(actual_output_width bits))
  }

  val cordic = CordicAtan()

  cordic.io.xy << io.cartesian.translateInto(cordic.io.xy.clone())((to, from) => {
    val w = cordic.io.xy.payload.data_width / 2

    val re = (from.re.sign) ? -from.re | from.re
    val im = (from.re.sign) ? -from.im | from.im

    to.data := im.resize(w) ## re.resize(w)
    to.user := 0
  })

  io.dout << cordic.io.dout.map(_.data.asSInt.resize(io.dout.payload.getWidth))
}

object CordicAtanWrapperVerilog extends App {
  Config.spinal.generateVerilog(CordicAtanWrapper())
}
