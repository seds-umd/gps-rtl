package gps

import spinal.core._
import spinal.lib._

/** Board-neutral serial-to-acquisition core; no board pins or host transport. */
case class GpsTop(freq_shift: Int = 24) extends Component {
  val io = new Bundle {
    // MAX2769 interface
    val clk_ser = in Bool ()
    val data_in = in UInt (1 bit)
    val data_sync = in Bool ()
    val time_sync = in Bool ()

    val results = master Stream (AcquisitionResults(12))
    val sample_overflow = out Bool ()
  }

  val sample_period = 4092
  val acq = AcquisitionModular(iq_size = 2, fft_size = 4096,
    freq_shift = freq_shift, period = sample_period, debug = false)
  val max = MaxInterface(iq_size = 2, period = sample_period)

  max.io.clk_ser <> io.clk_ser
  max.io.data_in <> io.data_in
  max.io.data_sync <> io.data_sync
  max.io.time_sync <> io.time_sync

  // The RF source cannot pause. Drain the serial FIFO while acquisition is
  // busy so the next window cannot begin with queued samples from an old epoch.
  // Treat this boundary as a live sample flow: only samples accepted by the
  // acquisition core are retained. Do not gate valid with ready, because the
  // core can compute ready from valid when joining the sample and PRN streams.
  max.io.iq.ready := True
  acq.io.iq.valid := max.io.iq.valid
  acq.io.iq.payload := max.io.iq.payload.asBits
  io.results << acq.io.results
  io.sample_overflow := max.io.overflow
}

object GpsTopSimVerilog extends App {
  Config.spinal.generateVerilog(GpsTop(freq_shift = 2).setDefinitionName("GpsTopSim"))
}

object GpsTopVerilog extends App {
  Config.spinal.generateVerilog(GpsTop())
}
