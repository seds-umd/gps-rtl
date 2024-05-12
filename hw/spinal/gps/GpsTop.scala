package gps

import spinal.core._

case class GpsTop() extends Component {
  val io = new Bundle {
    // MAX2769 interface
    val clk_ser = in Bool ()
    val data_in = in UInt (1 bit)
    val data_sync = in Bool ()
    val time_sync = in Bool ()

    val debug_out = out Bits ()
  }

  val acq = AcquisitionModular(2, 4096)
  val max = MaxInterface(2)

  max.io.clk_ser <> io.clk_ser
  max.io.data_in <> io.data_in
  max.io.data_sync <> io.data_sync
  max.io.time_sync <> io.time_sync

  acq.io.iq << max.io.iq

  io.debug_out <> acq.io.debug_synth_fft_index ## acq.io.debug_synth_fft_val ## acq.io.debug_synth_fft_freq
}

object GpsTopVerilog extends App {
  Config.spinal.generateVerilog(GpsTop())
}
