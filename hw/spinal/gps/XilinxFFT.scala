package gps

import spinal.core._
import spinal.lib._
import spinal.lib.bus.amba4.axis.{Axi4Stream, Axi4StreamConfig}

case class XilinxFFT() extends BlackBox {
  val data_in_config = Axi4StreamConfig(
    dataWidth = 2,
    useLast = true
  )

  val data_out_config = data_in_config.copy(userWidth = 4, useUser = true)

  val control_config = Axi4StreamConfig(
    dataWidth = 1
  )

  val io = new Bundle {
    val aclk = in Bool ()
    val aresetn = in Bool ()
    val aclken = in Bool ()

    val s_axis_config = slave(Axi4Stream(control_config))
    val s_axis_data = slave(Axi4Stream(data_in_config))
    val m_axis_data = master(Axi4Stream(data_out_config))
    val m_axis_status = master(Axi4Stream(control_config))
  }

  noIoPrefix()
  mapCurrentClockDomain(io.aclk, io.aresetn, io.aclken, LOW)

  private def renameIO(): Unit = {
    io.flatten.foreach(bt => {
      if (bt.getName().contains("valid")) bt.setName(bt.getName().replace("valid", "tvalid"))
      if (bt.getName().contains("ready")) bt.setName(bt.getName().replace("ready", "tready"))
      if (bt.getName().contains("payload_data")) bt.setName(bt.getName().replace("payload_data", "tdata"))
      if (bt.getName().contains("payload_last")) bt.setName(bt.getName().replace("payload_last", "tlast"))
      if (bt.getName().contains("payload_user")) bt.setName(bt.getName().replace("payload_user", "tuser"))
    })
  }

  addPrePopTask(() => renameIO())
}
