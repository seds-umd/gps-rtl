package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

// TODO:
// Make cordic phase and output width configurable
// Time multiplex CORDIC

case class TrackingChannel(
    iq_size: Int = 2,
    period: Int = 4092,
    fft_len_bits: Int = 12,
    fine_acq_factor_bits: Int = 3,
    debug: Boolean = false
) extends Component {
  val phase_bits = 10
  val dec_bits = 14

  val io = new Bundle {
    val iq = slave Stream (ComplexTimestamp(iq_size, period))

    // Config
    val config = slave Flow (AcquisitionResults())

    // Status
    val lost_lock = out Bool ()

    // Output
    val nav_data = master Stream (Bool())
  }

  // Same conversion as in acquisition, unbiases input and converts to 8 bits
  val iq_biased = io.iq.translateInto(Stream(ComplexTimestamp(8)))((to, from) => {
    to.c.re := from.c.re @@ U"6'b100000"
    to.c.im := from.c.im @@ U"6'b100000"
    to.t := from.t
  })

  // Carrier generation
  val cordic = CordicWrapper()
  val carrier_phase = Reg(UInt(phase_bits bits)) init 0
  val carrier_freq_est = Reg(SFix(8 exp, 16 bits)) // in units of ~125 Hz
  cordic.io.phase.payload := carrier_phase

  // Phase increments by freq / ts
  // ts is period of individual sample, 1/4.092MHz
  val carrier_phase_inc = carrier_freq_est >> (fft_len_bits + fine_acq_factor_bits - phase_bits)
  val carrier_phase_rem = Reg(carrier_phase_inc.clone())
  val carrier_phase_next = (carrier_phase_inc + carrier_phase_rem).toSInt

  when(cordic.io.phase.fire) {
    carrier_phase := (carrier_phase.asSInt + carrier_phase_next.resized).asUInt
    carrier_phase_rem.raw := (carrier_phase_inc + carrier_phase_rem).raw - (carrier_phase_next << -carrier_phase_rem.minExp)
  }

  // Carrier mixing
  val carrier_mixer = MixerTimestamp(8)
  carrier_mixer.io.input_a << iq_biased.addFragmentLast(False)
  carrier_mixer.io.input_b << cordic.io.dout.addFragmentLast(False)

  // Code mixing
  val code_phase = Reg(UInt(log2Up(period) bits))
  val prn =
    RemovePrn(
      iqInWidth = 8,
      iqOutWidth = 8,
      period = period,
      phaseWidth = 12,
      sampleRate = 4.092 MHz,
      earlyLate = true,
      debug = debug
    )
  val sv = Reg(UInt(6 bits)) init 0
  prn.io.sv := sv
  prn.io.set := Delay(io.config.fire, 1)
  prn.io.phase_offset := code_phase
  prn.io.input << carrier_mixer.io.output.toStreamOfFragment

  // Configure acquisition settings
  when(io.config.fire) {
    sv := io.config.sv
    code_phase := io.config.phase_offset

    // Truncate because frequency offset is always a small value
    carrier_freq_est := io.config.freq_offset.toSFix.truncated
    carrier_phase := 0
    carrier_phase_rem := 0
  }

  // Decimation
  val dec_early = Decimate(factor = period, iq_out_size = dec_bits)
  val dec_prompt = Decimate(factor = period, iq_out_size = dec_bits)
  val dec_late = Decimate(factor = period, iq_out_size = dec_bits)

  // Use prompt stream arbitration for all 3 streams
  val dec_fork = StreamFork(prn.io.prompt, 3, false)
  dec_early.io.iq_in << dec_fork(0).translateWith(prn.io.early)
  dec_prompt.io.iq_in << dec_fork(1)
  dec_late.io.iq_in << dec_fork(2).translateWith(prn.io.late)

  val dec_prompt_vec = StreamFork(dec_prompt.io.iq_out, 2, true)
  val early_late = StreamJoin(dec_early.io.iq_out, dec_late.io.iq_out)

  // Digitize output
  io.nav_data << dec_prompt_vec(0).map(_.re.sign)

  // Carrier PLL
  val carrier_pll = Pll(bw = 10f, gain = 0.25f)

  // Carrier discriminator - sign(I) * Q
  carrier_pll.io.err << dec_prompt_vec(1).translateInto(carrier_pll.io.err.clone())((to, from) => {
    when(~from.re.sign) {
      to.raw := -from.im.sat(widthOf(from.im) - widthOf(to.raw)) / 2
    } otherwise {
      to.raw := from.im.sat(widthOf(from.im) - widthOf(to.raw)) / 2
    }
  })

  carrier_pll.io.nco.ready := True
  when(carrier_pll.io.nco.fire) {
    carrier_freq_est := (carrier_freq_est + (carrier_pll.io.nco.payload >> 5)).truncated
  }

  // Noncoherent discriminator - sim only version
  // val early_power = dec_early.io.iq_out.re.clone()
  // val late_power = dec_late.io.iq_out.re.clone()

  // early_power := dec_early.io.iq_out.re*dec_early.io.iq_out.re - dec_early.io.iq_out.im*dec_early.io.iq_out.im + 2 * dec_early.io.iq_out.re * dec_early.io.iq_out.im
  // late_power := dec_late.io.iq_out.re*dec_late.io.iq_out.re - dec_late.io.iq_out.im*dec_late.io.iq_out.im + 2 * dec_late.io.iq_out.re * dec_late.io.iq_out.im

  // val code_err = (early_power - late_power)/(early_power + late_power)
  // Code DLL
  // val code_dll = Pll(bw = 1f, gain = 1f)
  // code_dll.io.err << early_late.translateWith((code_err.toSFix >> 7).truncated)

  // io.lost_lock := !(carrier_pll.io.locked && code_dll.io.locked)

  ////////////// Temp stuff to just make it compile

  early_late.ready := True

  // dec_early.io.iq_out.freeRun()
  // dec_prompt.io.iq_out.freeRun()
  // dec_late.io.iq_out.freeRun()

  io.lost_lock := False

  // To fix simulation issue
  val running = Reg(Bool()) init False

  when(io.iq.valid) {
    running := True
  }

  cordic.io.phase.valid := running

  // Debugging signals, will get optimized out
  val frequency_stream = Flow(SFix(8 exp, 16 bits))
  frequency_stream.payload := carrier_freq_est
  frequency_stream.valid := False
  when(carrier_pll.io.nco.fire) {
    frequency_stream.valid := True
  }
}

object TrackingChannelVerilog extends App {
  Config.spinal.generateVerilog(TrackingChannel(debug = true))
}
