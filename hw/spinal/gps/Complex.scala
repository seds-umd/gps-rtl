package gps

import spinal.core._

// n is number of bits per IQ components, ie n=2 means entire IQ sample is 4 bits wide
case class Complex(n : Int) extends Bundle {
    val im = SInt(n bits)
    val re = SInt(n bits)

    override def clone = new Complex(n)
}
