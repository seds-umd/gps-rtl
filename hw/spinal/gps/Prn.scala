package gps

import spinal.core._
import spinal.lib._

// Increment is 2^16/samples per chip
case class Prn() extends Component {
  val io = new Bundle {
    // Configuration
    val set = in Bool ()
    val sv = in UInt (6 bits) // An input of 0 means SV 1
    val inc = in UInt (17 bits)

    // Output
    val code = master Stream (Bool())
    val code_count = out UInt (10 bits)
    val sample_count = out UInt (12 bits)
  }

  val chip_fraction = Reg(UInt(16 bits)) init U"16'h8000"
  val increment = Reg(UInt(17 bits)) init 0
  val chip_fraction_next = chip_fraction +^ increment
  val advance_code = chip_fraction_next(16) & io.code.fire

  val code_count = Counter(1023, advance_code)
  val sample_count = Counter(4 * 1023, io.code.ready) // TODO: don't hard code sample rate

  io.code_count <> code_count
  io.sample_count <> sample_count

  // Absolute sample count for debugging. Will be optimized out in synthesis.
  val debug_count = Counter(64 bits, io.code.fire)

  when(io.set) {
    chip_fraction := U"16'h8000"
    increment := io.inc

    code_count.clear()
    sample_count.clear()
    debug_count.clear()
  } elsewhen (io.code.ready) {
    chip_fraction := chip_fraction_next(15 downto 0)
  }

  // Code generation
  val g1 = Reg(Bits(10 bits)) init B"10'h3FF"
  val g1_new = g1(3 - 1) ^ g1(10 - 1)

  val g2 = Reg(Bits(10 bits)) init B"10'h3FF"
  val g2_new = g2(2 - 1) ^ g2(3 - 1) ^ g2(6 - 1) ^ g2(8 - 1) ^ g2(9 - 1) ^ g2(10 - 1)

  val g2_tap1, g2_tap2 = Reg(UInt(4 bits)) init 0
  val g2i = g2(g2_tap1 - 1) ^ g2(g2_tap2 - 1)
  io.code.payload := g2i ^ g1(10 - 1)
  io.code.valid := ~io.set & ~(g2_tap1 === 0)

  // Set taps
  when(io.set) {
    switch(io.sv + 1) {
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

  when(advance_code & !io.set) {
    g1 := g1(8 downto 0) ## g1_new
    g2 := g2(8 downto 0) ## g2_new
  }
}

object PrnVerilog extends App {
  Config.spinal.generateVerilog(Prn())
}
