package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

// TODO:
// Time multiplex CORDIC

case class TrackingChannel(config: GpsConfig) extends Component {
  val io = new Bundle {
    val iq = slave Stream (ComplexTimestamp(config.max_iq_size, config.prn_period))
    val config_flow = slave Flow (AcquisitionResults())

    val lost_lock = out Bool ()
    val nav_data = master Stream (Bool())

    val debug = master Flow (TrackingDebugReg(config))

    // Debugging
    val fb_enabled = in Bool ()
  }

  // Same conversion as in acquisition, unbiases input and converts to 8 bits
  val iq_biased = io.iq.translateInto(Stream(ComplexTimestamp(8)))((to, from) => {
    to.c.re := from.c.re @@ U"6'b100000"
    to.c.im := from.c.im @@ U"6'b100000"
    to.t := from.t
  })

  // Carrier generation
  val cordic_sincos = CordicSinCosWrapper()
  val carrier_phase = Reg(UInt(config.sincos_phase_actual_bits bits)) init 0
  val carrier_freq_est = Reg(SFix(8 exp, 16 bits)) // in units of ~125 Hz
  cordic_sincos.io.phase.payload := carrier_phase

  // Phase increments by freq / ts
  // ts is period of individual sample, 1/4.092MHz
  val carrier_phase_inc =
    carrier_freq_est >> (config.fft_bits + config.fine_acq_factor_log - config.sincos_phase_actual_bits)
  val carrier_phase_rem = Reg(carrier_phase_inc.clone())
  val carrier_phase_next = (carrier_phase_inc + carrier_phase_rem).toSInt

  when(cordic_sincos.io.phase.fire) {
    carrier_phase := (carrier_phase.asSInt - carrier_phase_next.resized).asUInt
    carrier_phase_rem.raw := (carrier_phase_inc + carrier_phase_rem).raw - (carrier_phase_next << -carrier_phase_rem.minExp)
  }

  // Carrier mixing
  val carrier_mixer = MixerTimestamp(8)
  carrier_mixer.io.input_a << iq_biased.addFragmentLast(False).stage()
  carrier_mixer.io.input_b << cordic_sincos.io.dout.addFragmentLast(False)

  // Code mixing
  val code_phase = Reg(UInt(config.fft_bits bits))// init 0
  val prn =
    RemovePrn(
      input_width = 8,
      config = config
    )
  val sv = Reg(UInt(6 bits)) init 0
  prn.io.set := Delay(io.config_flow.fire, 1)
  prn.io.sv := io.config_flow.sv
  prn.io.phase_offset := io.config_flow.phase_offset
  prn.io.input << carrier_mixer.io.output.toStreamOfFragment

  // Configure acquisition settings
  when(io.config_flow.fire) {
    sv := io.config_flow.sv
    code_phase := io.config_flow.phase_offset

    // Truncate because frequency offset is always a small value
    carrier_freq_est := io.config_flow.freq_offset.toSFix.truncated
    carrier_phase := 0
    carrier_phase_rem := 0
  }

  // Decimation
  val dec_early = Decimate(factor = config.prn_period, iq_out_size = config.dec_width)
  val dec_prompt = Decimate(factor = config.prn_period, iq_out_size = config.dec_width)
  val dec_late = Decimate(factor = config.prn_period, iq_out_size = config.dec_width)

  val prn_removed = StreamFork(prn.io.output, 3, true)
  dec_early.io.iq_in << prn_removed(0).map(_(0))
  dec_prompt.io.iq_in << prn_removed(1).map(_(1))
  dec_late.io.iq_in << prn_removed(2).map(_(2))

  val dec_prompt_vec = StreamFork(dec_prompt.io.iq_out, 2, true)
  val early_late = StreamJoin(dec_early.io.iq_out, dec_late.io.iq_out)

  // Digitize output
  io.nav_data << dec_prompt_vec(0).map(_.re.sign)

  // Carrier PLL
  val carrier_pll = Pll(config.carrier_pll_config)

  // Carrier discriminator - sign(I) * Q
  // carrier_pll.io.err << dec_prompt_vec(1).translateInto(carrier_pll.io.err.clone())((to, from) => {
  //   when(from.re.sign) {
  //     to.raw := -from.im.sat(widthOf(from.im) - widthOf(to.raw)) / 2
  //   } otherwise {
  //     to.raw := from.im.sat(widthOf(from.im) - widthOf(to.raw)) / 2
  //   }
  // })

  // atan discriminator
  val cordic_atan = CordicAtanWrapper()
  cordic_atan.io.cartesian << dec_prompt_vec(1).translateInto(cordic_atan.io.cartesian.clone())((to, from) => {
    to.re := from.re.sat(from.re.getWidth - to.re.getWidth)
    to.im := from.im.sat(from.im.getWidth - to.im.getWidth)
  })
  carrier_pll.io.err << cordic_atan.io.dout.map((angle) => {
    val x = carrier_pll.io.err.payload.clone()
    // x.raw := angle.roundToInf(1) / 2
    x.raw := (angle ## B(0, x.raw.getWidth-angle.getWidth bits)).asSInt / 2
    x
  })

  carrier_pll.io.nco.ready := True
  when(carrier_pll.io.nco.fire && io.fb_enabled) {
    carrier_freq_est := (carrier_freq_est + (carrier_pll.io.nco.payload >> 5)).truncated
  }

  // Code DLL
  val code_dll = Pll(config.code_pll_config)
  code_dll.io.err << early_late.translateInto(code_dll.io.err.clone())((to, from) => {
    val early = from._1
    val late = from._2

    // Noncoherent discriminator - sim only version
    // val early_power = early.re * early.re - early.im * early.im + 2 * early.re * early.im
    // val late_power = late.re * late.re - late.im * late.im + 2 * late.re * late.im
    // val err = ((early_power - late_power) << 7) / (early_power + late_power)
    // val err = ((early_power - late_power) << 7)

    val err = early.re - early.im

    to.raw := err.sat(err.getWidth - to.raw.getWidth)
  })
  code_dll.io.nco.freeRun()

  // io.lost_lock := !(carrier_pll.io.locked && code_dll.io.locked)

  ////////////// Temp stuff to just make it compile

  io.lost_lock := False

  // To fix simulation issue
  val running = Reg(Bool()) init False

  when(io.iq.valid) {
    running := True
  }

  cordic_sincos.io.phase.valid := running

  // Debugging signals, will get optimized out
  val frequency_stream = Flow(SFix(8 exp, 16 bits))
  frequency_stream.payload := carrier_freq_est
  frequency_stream.valid := False
  when(carrier_pll.io.nco.fire) {
    frequency_stream.valid := True
  }

  val debug_area = new Area {
    val debug_reg = Reg(TrackingDebugReg(config)) init TrackingDebugReg(config).getZero
    val debug_reg_valid = Reg(Bits(7 bits)) init 0

    io.debug.payload := debug_reg
    io.debug.valid := debug_reg_valid.andR

    when(io.debug.fire) {
      debug_reg_valid := 0
    }

    when(dec_early.io.iq_out.fire) {
      debug_reg.dec_early := dec_early.io.iq_out.payload
      debug_reg_valid(0) := True
    }

    when(dec_prompt.io.iq_out.fire) {
      debug_reg.dec_prompt := dec_prompt.io.iq_out.payload
      debug_reg_valid(1) := True
    }

    when(dec_late.io.iq_out.fire) {
      debug_reg.dec_late := dec_late.io.iq_out.payload
      debug_reg_valid(2) := True
    }

    when(carrier_pll.io.err.fire) {
      debug_reg.carr_err := carrier_pll.io.err.payload
      debug_reg_valid(3) := True
    }

    when(carrier_pll.io.nco.fire) {
      debug_reg.carr_nco := carrier_pll.io.nco.payload
      debug_reg_valid(4) := True
    }

    when(code_dll.io.err.fire) {
      debug_reg.code_err := code_dll.io.err.payload
      debug_reg_valid(5) := True
    }

    when(code_dll.io.nco.fire) {
      debug_reg.code_nco := code_dll.io.nco.payload
      debug_reg_valid(6) := True
    }
  }
}

case class TrackingDebugReg(config: GpsConfig) extends Bundle {
  val dec_early = Complex(config.dec_width)
  val dec_prompt = Complex(config.dec_width)
  val dec_late = Complex(config.dec_width)
  val carr_err = SFix(config.pll_err_peak exp, config.pll_width bits)
  val carr_nco = SFix(config.carrier_pll_nco_peak exp, config.pll_width bits)
  val code_err = SFix(config.pll_err_peak exp, config.pll_width bits)
  val code_nco = SFix(config.code_pll_nco_peak exp, config.pll_width bits)
}

object TrackingChannelVerilog extends App {
  val gps_config = GpsConfig(debug = true)
  Config.spinal.generateVerilog(TrackingChannel(gps_config))
}
