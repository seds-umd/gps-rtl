package gps

import spinal.core._
import spinal.lib._

/* Code frequency math:
 *
 * Nominal frequency: 1.023 MHz
 * inc = f_code / f_samp * 2^width
 * f_code = inc * f_samp / 2^width
 * inc LSB = 1 * f_samp / 2^width
 *
 * 16b: 62.4 Hz
 * 20b: 3.90 Hz
 * 24b: 0.244 Hz
 * 28b: 15.2 mHz
 *
 * Frequency adjust range of at least 100ppm = width - 13, -12 for signed
 */

// nom_ratio is f_code / f_samp = 1/4 for f_samp=4.092 MHz
case class Prn(counter_width: Int = 28, nom_ratio: Double = 1 / 4) extends Component {
  val io = new Bundle {
    // Configuration
    val sv = slave Flow (UInt(6 bits)) // Offset by 1, 0 means SV 1
    val ratio = in UFix (1 exp, counter_width + 1 bits)
    val freq_adj = slave Flow (SInt(counter_width - 12 bits))

    // Output
    val code = master Stream (Bool())
    val code_count = out UInt (10 bits)
    val sample_count = out UInt (12 bits)
  }

  val inc_base = Reg(UInt(counter_width + 1 bits)) init U(((1 << counter_width) * nom_ratio).toInt)
  val inc_delta = Reg(SInt(counter_width - 12 bits)) init 0
  val inc_sum = inc_base + inc_delta.resize(counter_width + 1 bits).asUInt

  val chip_fraction = Reg(UInt(counter_width bits)) init U(1 << (counter_width - 1))
  val chip_fraction_next = chip_fraction +^ inc_sum
  val advance_code = chip_fraction_next(counter_width) & io.code.fire

  val code_count = Counter(1023, advance_code)
  val sample_count = Counter(4 * 1023, io.code.fire) // TODO: don't hard code sample rate

  io.code_count <> code_count
  io.sample_count <> sample_count

  // Absolute sample count for debugging. Will be optimized out in synthesis.
  val debug_count = Counter(32 bits, io.code.fire)

  when(io.sv.fire) {
    chip_fraction := U(1 << (counter_width - 1))
    inc_base := io.ratio.raw

    code_count.clear()
    sample_count.clear()
    debug_count.clear()
  } elsewhen (io.code.fire) {
    chip_fraction := chip_fraction_next.trim(2)
  }

  when(io.freq_adj.fire) {
    inc_delta := io.freq_adj.payload
  }

  // Code generation
  val g1 = Reg(Bits(10 bits)) init B"10'h3FF"
  val g1_new = g1(3 - 1) ^ g1(10 - 1)

  val g2 = Reg(Bits(10 bits)) init B"10'h3FF"
  val g2_new = g2(2 - 1) ^ g2(3 - 1) ^ g2(6 - 1) ^ g2(8 - 1) ^ g2(9 - 1) ^ g2(10 - 1)

  val g2_tap1, g2_tap2 = Reg(UInt(4 bits)) init 0
  val g2i = g2(g2_tap1 - 1) ^ g2(g2_tap2 - 1)
  io.code.payload := g2i ^ g1(10 - 1)
  io.code.valid := ~io.sv.fire & ~(g2_tap1 === 0)

  // Set taps
  when(io.sv.fire) {
    switch(io.sv.payload + 1) {
      is(1)(g2_tap1 := 2, g2_tap2 := 6)
      is(2)(g2_tap1 := 3, g2_tap2 := 7)
      is(3)(g2_tap1 := 4, g2_tap2 := 8)
      is(4)(g2_tap1 := 5, g2_tap2 := 9)
      is(5)(g2_tap1 := 1, g2_tap2 := 9)
      is(6)(g2_tap1 := 2, g2_tap2 := 10)
      is(7)(g2_tap1 := 1, g2_tap2 := 8)
      is(8)(g2_tap1 := 2, g2_tap2 := 9)
      is(9)(g2_tap1 := 3, g2_tap2 := 10)
      is(10)(g2_tap1 := 2, g2_tap2 := 3)
      is(11)(g2_tap1 := 3, g2_tap2 := 4)
      is(12)(g2_tap1 := 5, g2_tap2 := 6)
      is(13)(g2_tap1 := 6, g2_tap2 := 7)
      is(14)(g2_tap1 := 7, g2_tap2 := 8)
      is(15)(g2_tap1 := 8, g2_tap2 := 9)
      is(16)(g2_tap1 := 9, g2_tap2 := 10)
      is(17)(g2_tap1 := 1, g2_tap2 := 4)
      is(18)(g2_tap1 := 2, g2_tap2 := 5)
      is(19)(g2_tap1 := 3, g2_tap2 := 6)
      is(20)(g2_tap1 := 4, g2_tap2 := 7)
      is(21)(g2_tap1 := 5, g2_tap2 := 8)
      is(22)(g2_tap1 := 6, g2_tap2 := 9)
      is(23)(g2_tap1 := 1, g2_tap2 := 3)
      is(24)(g2_tap1 := 4, g2_tap2 := 6)
      is(25)(g2_tap1 := 5, g2_tap2 := 7)
      is(26)(g2_tap1 := 6, g2_tap2 := 8)
      is(27)(g2_tap1 := 7, g2_tap2 := 9)
      is(28)(g2_tap1 := 8, g2_tap2 := 10)
      is(29)(g2_tap1 := 1, g2_tap2 := 6)
      is(30)(g2_tap1 := 2, g2_tap2 := 7)
      is(31)(g2_tap1 := 3, g2_tap2 := 8)
      is(32)(g2_tap1 := 4, g2_tap2 := 9)
      default(g2_tap1 := 1, g2_tap2 := 1) // Shouldn't ever happen
    }

    g1 := B"10'h3FF"
    g2 := B"10'h3FF"
  }

  when(advance_code & !io.sv.fire) {
    g1 := g1(8 downto 0) ## g1_new
    g2 := g2(8 downto 0) ## g2_new
  }
}

object PrnVerilog extends App {
  Config.spinal.generateVerilog(Prn())
}
