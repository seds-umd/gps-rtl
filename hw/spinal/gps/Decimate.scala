package gps

import spinal.core._
import spinal.lib._

case class Decimate(
    iq_in_size: Int = 8,
    iq_out_size: Int = 8,
    factor: Int = 8
) extends Component {
  val io = new Bundle {
    val iq_in = slave Stream (Complex(iq_in_size))
    val iq_out = master Stream (Complex(iq_out_size))
  }

  val iq_in = io.iq_in.payload

  val dec_counter = Counter(factor + 1) init 0
  val dec_size = iq_in_size + log2Up(factor)
  val dec_sample = Reg(Complex(dec_size)) init Complex(dec_size).getZero
  val dec_out = Complex(iq_out_size)

  dec_out.re := dec_sample.re >> (log2Up(factor) + iq_in_size - iq_out_size)
  dec_out.im := dec_sample.im >> (log2Up(factor) + iq_in_size - iq_out_size)

  io.iq_in.ready := dec_counter < factor
  io.iq_out.valid := dec_counter === factor
  io.iq_out.payload := dec_out

  // If input is valid and we're still waiting on samples
  when(io.iq_in.fire & dec_counter < factor) {
    dec_sample.re := dec_sample.re + iq_in.re
    dec_sample.im := dec_sample.im + iq_in.im

    dec_counter.increment()
  }

  // Wait for output to be consumed
  when(io.iq_out.fire) {
    dec_sample.re := 0
    dec_sample.im := 0

    dec_counter.clear()
  }
}

object DecimateVerilog extends App {
  Config.spinal.generateVerilog(Decimate())
}
