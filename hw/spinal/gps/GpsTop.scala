package gps

import spinal.core._

case class GpsTop(config: GpsConfig) extends Component {
  val io = new Bundle {
    // MAX2769 interface
    val clk_ser = in Bool ()
    val data_in = in UInt (1 bit)
    val data_sync = in Bool ()
    val time_sync = in Bool ()

    val debug_out = out Bits ()
  }

  val acq = AcquisitionModular(config)
  val max = MaxInterface(2)

  max.io.max.clk_ser <> io.clk_ser
  max.io.max.data_in <> io.data_in
  max.io.max.data_sync <> io.data_sync
  max.io.max.time_sync <> io.time_sync

  acq.io.iq << max.io.iq.translateInto(acq.io.iq.clone())((to, from) => {
    to := from.asBits
  })

  io.debug_out := acq.io.results.sv ## acq.io.results.snr.trim(1)
  acq.io.results.ready := True
}

object GpsTopVerilog extends App {
  val gps_config = GpsConfig()

  Config.spinal.generateVerilog(GpsTop(gps_config))
}
