package gps

import spinal.core._

case class GpsConfig(
    // Set by MAX2769 register config
    max_iq_size: Int = 2,

    // Process 1ms at a time at fs=4.092 MHz
    prn_period: Int = 4092,

    // From 1ms acquisition period, 2^3=8 fine acquisition factor gives 125 MHz resolution
    fine_acq_factor_log: Int = 3,

    // Tells RemovePrn that sampling frequency is not real
    debug: Boolean = false,

    // Widths of sincos cordic in cordic_sincos.tcl
    sincos_phase_bits: Int = 12,
    sincos_out_bits: Int = 9,

    // Widths of atan cordic in cordic_atan.tcl
    atan_in_bits: Int = 12,
    atan_out_bits: Int = 9,

    // User width in both cordics
    cordic_user_width: Int = 4,

    // PLL settings
    carrier_pll_bw: Float = 10f,
    carrier_pll_gain: Float = 0.25f,
    code_pll_bw: Float = 1f,
    code_pll_gain: Float = 1f,
    pll_zeta: Float = 0.707f,
    pll_ts: Float = 1e-3f,
    pll_width: Int = 8,
    pll_err_peak: Int = 0,
    pll_nco_peak: Int = 3,

    // Decimated sample width
    dec_width: Int = 14,
) {
  def fft_bits = log2Up(prn_period)
  def fine_acq_factor = Math.pow(2, fine_acq_factor_log)

  def sincos_phase_actual_bits = sincos_phase_bits - 2
  def sincos_out_actual_bits = sincos_out_bits - 1

  def carrier_pll_config = PllConfig(
    bw = carrier_pll_bw,
    gain = carrier_pll_gain,
    zeta = pll_zeta,
    ts = pll_ts,
    width = pll_width,
    err_peak = pll_err_peak,
    nco_peak = pll_nco_peak
  )
  def code_pll_config = PllConfig(
    bw = code_pll_bw,
    gain = code_pll_gain,
    zeta = pll_zeta,
    ts = pll_ts,
    width = pll_width,
    err_peak = pll_err_peak,
    nco_peak = pll_nco_peak
  )
}
