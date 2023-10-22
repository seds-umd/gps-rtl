package gps

import spinal.core._

case class ComplexTimestamp(size_c: Int = 2, period: Int = 4092) extends Bundle {
    val c = Complex(size_c)
    val t = UInt(log2Up(period) bits)

    override def clone = new ComplexTimestamp(size_c, period)
}
