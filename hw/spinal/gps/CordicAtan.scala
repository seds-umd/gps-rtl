package gps

import spinal.core._
import spinal.lib._

import ethernet.Utils

case class CordicAtan() extends BlackBox {
  val io = new Bundle {
    val aclk = in Bool ()
    val aresetn = in Bool ()

    val xy = slave Stream(new CordicBundle(32, 3))
    val dout = master Stream(new CordicBundle(16, 3))
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
