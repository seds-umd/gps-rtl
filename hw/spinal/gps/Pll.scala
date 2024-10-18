package gps

import spinal.core._
import spinal.lib._

// TODO:
// Make loop params runtime configurable?
// Are loop param equations optimal?
// Make it more synthesize - multiplex muls to use a single DSP (and possibly even an external one)

case class Pll(bw: Float, gain: Float, zeta: Float = 0.707f, ts: Float = 1e-3f) extends Component {
  val w_n = 8 * zeta * bw / (4 * zeta * zeta + 1)
  val tau1 = gain / (w_n * w_n)
  val tau2 = 2 * zeta / w_n
  val _c1 = tau2 / tau1
  val _c2 = ts / tau1

  printf("tau1=%f, tau2=%f\n", tau1, tau2)
  printf("C1=%f, C2=%f\n", _c1, _c2)

  val width = 8 bits

  val io = new Bundle {
    // err is +-1, 0 exp covers entire range
    val err = slave Stream (SFix(0 exp, width))

    // higher nco peak means faster slew rate but more noise at steady state
    val nco = master Stream (SFix(3 exp, width))

    val locked = out Bool ()
  }

  val c1 = SFix(log2Up(_c1.toInt) + 1 exp, 8 bits)
  val c2 = SFix(log2Up(_c2.toInt) + 1 exp, 8 bits)
  c1 := _c1
  c2 := _c2

  val last_err = Reg(io.err.payload.clone()) init 0
  val last_nco = Reg(io.nco.payload.clone()) init 0

  val t1 = c1 * (io.err.payload - last_err)
  val t2 = c2 * io.err.payload
  val nco_full = t1 + t2

  val nco_sat = io.nco.payload.clone()

  // Saturate output
  when(nco_full > nco_sat.maxValue) {
    nco_sat := nco_sat.maxValue
  } elsewhen (nco_full < nco_sat.minValue) {
    nco_sat := nco_sat.minValue
  } otherwise {
    nco_sat := nco_full.truncated
  }

  io.nco << io.err.translateWith(nco_sat)

  when(io.err.fire) {
    last_err := io.err.payload
  }

  when(io.nco.fire) {
    last_nco := io.nco.payload
  }

  // Locked after 128 cycles (128 ms)
  val err_threshold = 0.1
  val lock_counter = CounterUpDown(256)
  val lock = ((last_err >= 0) && (last_err < err_threshold)) || ((last_err < 0) && (last_err > -err_threshold))
  io.locked := lock_counter > 128

  when(!lock && (lock_counter !== 0)) {
    lock_counter.decrement()
  } elsewhen (io.nco.fire && !lock_counter.mayOverflow) {
    lock_counter.increment()
  }
}

object PllVerilog extends App {
  val bw = 10f
  val gain = 0.25f

  Config.spinal.generateVerilog(Pll(bw, gain))
}
