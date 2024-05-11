package gps

import spinal.core._
import spinal.lib._

case class Mixer(width: Int = 8) extends Component {
  val io = new Bundle {
    val input_a = slave Stream Fragment(Complex(width))
    val input_b = slave Stream Fragment(Complex(width))
    val output = master Stream Fragment(Complex(width))
  }

  io.output.re.setAsReg()
  io.output.im.setAsReg()
  io.output.valid.setAsReg() init(False)
  io.output.last.setAsReg()

  // Pipeline advanced when previous stage is valid
  // Output ready skips pipeline to stall input bus

  val joined = StreamJoin(io.input_a, io.input_b)
  joined.ready := io.output.ready

  val s1_a = Reg(Complex(width))
  val s1_b = Reg(Complex(width))
  val s1_valid = Reg(Bool()) init False

  val s2_re_mix1 = Reg(SInt(16 bits))
  val s2_re_mix2 = Reg(SInt(16 bits))
  val s2_im_mix1 = Reg(SInt(16 bits))
  val s2_im_mix2 = Reg(SInt(16 bits))
  val s2_valid = Reg(Bool()) init False

  val s3_re_mix = Reg(SInt(16 bits))
  val s3_im_mix = Reg(SInt(16 bits))
  val s3_valid = Reg(Bool()) init False

  // Advance only when output is ready
  when(io.output.ready) {
    // Advance first stage
    when(joined.fire) {
      s1_a := joined.payload._1
      s1_b := joined.payload._2
      s1_valid := True
    } otherwise {
      s1_valid := False
    }

    // Advance second stage
    when(s1_valid) {
      s2_re_mix1 := s1_a.re * s1_b.re
      s2_re_mix2 := s1_a.im * s1_b.im
      s2_im_mix1 := s1_a.re * s1_b.im
      s2_im_mix2 := s1_a.im * s1_b.re
      s2_valid := True
    } otherwise {
      s2_valid := False
    }

    // Advance third stage
    when(s2_valid) {
      s3_re_mix := s2_re_mix1 - s2_re_mix2
      s3_im_mix := s2_im_mix1 + s2_im_mix2
      s3_valid := True
    } otherwise {
      s3_valid := False
    }

    // Truncate to 8 bits
    when(s3_valid) {
      io.output.re := s3_re_mix.round(8)
      io.output.im := s3_im_mix.round(8)
      io.output.valid := True
    } otherwise {
      io.output.valid := False
    }

    // Last is OR of both inputs
    val latency = LatencyAnalysis(io.input_a.valid, io.output.valid)
    io.output.last := Delay(io.input_a.last || io.input_b.last, latency - 1, io.output.ready, init = False)
  }
}

case class MixerWrapper() extends Component {
  val io = new Bundle {
    val input_a = slave Stream Fragment(Complex(8).asBits)
    val input_b = slave Stream Fragment(Complex(8).asBits)
    val output = master Stream Fragment(Complex(8).asBits)
  }

  val mixer = Mixer()

  mixer.io.input_a << io.input_a.translateInto(Stream(Fragment(Complex(8))))((to, from) => {
    to.fragment.assignFromBits(from.fragment)
    to.last := from.last
  })

  mixer.io.input_b << io.input_b.translateInto(Stream(Fragment(Complex(8))))((to, from) => {
    to.fragment.assignFromBits(from.fragment)
    to.last := from.last
  })

  io.output << mixer.io.output.translateInto(Stream(Fragment(Complex(8).asBits)))((to, from) => {
    to.fragment := from.fragment.asBits
    to.last := from.last
  })
}

object MixerVerilog extends App {
  Config.spinal.generateVerilog(MixerWrapper())
}
