package gps

import spinal.core._
import spinal.lib._

case class IqTriangleWave(width: Int = 2) extends Component {
  val io = new Bundle {
    val out = master Stream (Complex(width))
  }

  val re = Reg(SInt(width bits)) init 0
  val im = Reg(SInt(width bits)) init -(1 << (width - 1))

  io.out.re := re
  io.out.im := im
  io.out.valid := True

  when (io.out.fire) {
    re := re + 1
    im := im + 1
  }
}
