package gps

import spinal.core._

// Currently hard coded for alpha=61/64, beta=13/32

// alpha = 61/64 = 1 - 1/64 - 1/32 = 1 - (1 >> 6) - (1 >> 5)
// beta = 13/32 = 1/2 - 1/16 - 1/32

case class Magnitude() extends Component {
    val io = new Bundle {
        val re = in SInt(8 bits)
        val im = in SInt(8 bits)
        val ready = in Bool()

        val mag = out UInt(8 bits) // TODO: how many bits?
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

object MagnitudeVerilog extends App {
  Config.spinal.generateVerilog(Magnitude())
}
