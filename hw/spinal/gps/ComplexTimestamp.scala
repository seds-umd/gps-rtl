package gps

import spinal.core._
import spinal.lib._

case class ComplexTimestamp(size_c: Int = 2, period: Int = 4092) extends Bundle {
  val c = Complex(size_c)
  val t = UInt(log2Up(period) bits)

  override def clone = new ComplexTimestamp(size_c, period)
}

object ComplexTimestamper {
  def apply(input: Stream[Complex], period: Int = 4092): Stream[ComplexTimestamp] = {
    val timestamp_counter = Counter(period, input.fire)
    val ret = input.translateInto(Stream(ComplexTimestamp(input.payload.n, period)))((to, from) => {
      to.c := from
      to.t := timestamp_counter.value
    })
    ret
  }
}
