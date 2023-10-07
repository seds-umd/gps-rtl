package gps

import spinal.core._

// n is number of bits per IQ components, ie n=2 means entire IQ sample is 4 bits wide
case class IqBundle(n : Int) extends Bundle {
    val i = SInt(n bits)
    val q = SInt(n bits)

    override def clone = new IqBundle(n)
}
