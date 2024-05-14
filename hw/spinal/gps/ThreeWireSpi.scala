package gps

import spinal.core._

case class ThreeWireSpi() extends BlackBox {
    val io = new Bundle {
        val clk = in Bool()
        val rst = in Bool()

        // SPI
        val SCLK = out Bool()
        val CS = out Bool()
        val SDATA = out Bool()

        // Registers
        val reg = in Vec(UInt(28 bits), 8)
    }

    noIoPrefix()

    mapClockDomain(clock = io.clk, reset = io.rst)

    // Rename ports to match verilog names
    private def renameIO(): Unit = {
        io.flatten.foreach(bt => {
            if(bt.getName().contains("reg"))
                bt.setName(bt.getName().replace("_", ""))
        })
    }

    addPrePopTask(() => renameIO())

    addRTLPath("../../verilog/three_wire_spi.v")
}
