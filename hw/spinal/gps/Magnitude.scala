package gps

import spinal.core._
import spinal.lib._

// Currently hard coded for alpha=61/64, beta=13/32

// alpha = 61/64 = 1 - 1/64 - 1/32 = 1 - (1 >> 6) - (1 >> 5)
// beta = 13/32 = 1/2 - 1/16 - 1/32

case class Magnitude() extends Component {
  val io = new Bundle {
    val re = in SInt (8 bits)
    val im = in SInt (8 bits)
    val ready = in Bool ()

    val mag = out UInt (8 bits)
  }

  val s1_re_abs = RegNextWhen(io.re.abs, io.ready)
  val s1_im_abs = RegNextWhen(io.im.abs, io.ready)

  // Resize to 16 bits here so no precision is lost. This reduces average error by about 1/3.
  val s2_max = RegNextWhen((s1_re_abs > s1_im_abs) ? s1_re_abs | s1_im_abs, io.ready) << 8
  val s2_min = RegNextWhen((s1_re_abs > s1_im_abs) ? s1_im_abs | s1_re_abs, io.ready) << 8

  val s3_max_1 = RegNextWhen(s2_max, io.ready)
  val s3_max_1_64 = RegNextWhen(s2_max >> 6, io.ready)
  val s3_max_1_32 = RegNextWhen(s2_max >> 5, io.ready)
  val s3_min_1_2 = RegNextWhen(s2_min >> 1, io.ready)
  val s3_min_1_16 = RegNextWhen(s2_min >> 4, io.ready)
  val s3_min_1_32 = RegNextWhen(s2_min >> 5, io.ready)

  val s4_a = RegNextWhen(s3_max_1 - s3_max_1_32 - s3_max_1_64, io.ready)
  val s4_b = RegNextWhen(s3_min_1_2 - s3_min_1_16 - s3_min_1_32, io.ready)

  val s5_mag = RegNextWhen(s4_a + s4_b, io.ready)
  io.mag <> s5_mag(s5_mag.getWidth - 8, 8 bits)
}

case class MagnitudeStream(width: Int = 8) extends Component {
  val io = new Bundle {
    val input = slave Stream Fragment(Complex(width))
    val mag = master Stream Fragment(UInt(width bits))
  }

  io.input.ready := io.mag.ready

  val s1_re_abs = RegNextWhen(io.input.re.abs, io.mag.ready && io.input.fire)
  val s1_im_abs = RegNextWhen(io.input.im.abs, io.mag.ready && io.input.fire)
  val s1_valid = RegNextWhen(io.input.fire, io.mag.ready) init False

  // Resize to 16 bits here so no precision is lost. This reduces average error by about 1/3.
  val s2_max = RegNextWhen((s1_re_abs > s1_im_abs) ? s1_re_abs | s1_im_abs, io.mag.ready && s1_valid) << 8
  val s2_min = RegNextWhen((s1_re_abs > s1_im_abs) ? s1_im_abs | s1_re_abs, io.mag.ready && s1_valid) << 8
  val s2_valid = RegNextWhen(s1_valid, io.mag.ready) init False

  val s3_max_1 = RegNextWhen(s2_max, io.mag.ready && s2_valid)
  val s3_max_1_64 = RegNextWhen(s2_max >> 6, io.mag.ready && s2_valid)
  val s3_max_1_32 = RegNextWhen(s2_max >> 5, io.mag.ready && s2_valid)
  val s3_min_1_2 = RegNextWhen(s2_min >> 1, io.mag.ready && s2_valid)
  val s3_min_1_16 = RegNextWhen(s2_min >> 4, io.mag.ready && s2_valid)
  val s3_min_1_32 = RegNextWhen(s2_min >> 5, io.mag.ready && s2_valid)
  val s3_valid = RegNextWhen(s2_valid, io.mag.ready) init False

  val s4_a = RegNextWhen(s3_max_1 - s3_max_1_32 - s3_max_1_64, io.mag.ready && s3_valid)
  val s4_b = RegNextWhen(s3_min_1_2 - s3_min_1_16 - s3_min_1_32, io.mag.ready && s3_valid)
  val s4_valid = RegNextWhen(s3_valid, io.mag.ready) init False

  val s5_mag = RegNextWhen(s4_a + s4_b, io.mag.ready)
  val s5_valid = RegNextWhen(s4_valid, io.mag.ready) init False

  io.mag.payload := s5_mag.round(width)
  io.mag.valid := s5_valid

  val latency = LatencyAnalysis(io.input.valid, io.mag.valid)
  io.mag.last := Delay(io.input.last, latency, io.mag.ready, init = False)
}

case class MagnitudeStreamWrapper() extends Component {
  val io = new Bundle {
    val input = slave Stream Fragment(Complex(8).asBits)
    val mag = master Stream Fragment(UInt(8 bits))
  }

  val mag = MagnitudeStream()

  mag.io.input << io.input.translateInto(Stream(Fragment(Complex(8))))((to, from) => {
    to.fragment.assignFromBits(from.fragment)
    to.last := from.last
  })

  io.mag << mag.io.mag
}

object MagnitudeVerilog extends App {
  Config.spinal.generateVerilog(Magnitude())
}

object MagnitudeStreamVerilog extends App {
  Config.spinal.generateVerilog(MagnitudeStreamWrapper())
}
