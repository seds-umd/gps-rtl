package gps

import spinal.core._
import spinal.lib._
import spinal.lib.com.uart.Uart

case class UartTop() extends Component {
  val io = new Bundle {
    // MAX2769 interface
    val clk_ser = in Bool ()
    val data_in = in UInt (1 bit)
    val data_sync = in Bool ()
    val time_sync = in Bool ()

    // UART
    val uart = master(Uart())

    // Config SPI
    val SCLK = out Bool ()
    val CS = out Bool ()
    val SDATA = out Bool ()
  }

  val max = MaxInterface(iq_size = 2)
  max.io.clk_ser <> io.clk_ser
  max.io.data_in <> io.data_in
  max.io.data_sync <> io.data_sync
  max.io.time_sync <> io.time_sync

  val uart = UartControl(
    iqSize = 2,
    baud = 115200,
    memoryBits = 1800 * 1024
  )
  uart.io.uart <> io.uart
  uart.io.iq << max.io.iq.translateInto(Stream(Complex(2)))((to, from) => {
    to := from.c
  })

  val spi_config = Vec(
    U"hA2951A3", // CONF1
    U"h8550488", // CONF2
    U"hEAFE1DC", // CONF3
    U"h9EC0008", // PLLCONF
    U"h0C00080", // DIV
    U"h8000070", // FDIV
    U"h8000000", // RESERVED
    U"h400400B" // CLK
  )

  val spi = ThreeWireSpi()
  spi.io.SCLK <> io.SCLK
  spi.io.CS <> io.CS
  spi.io.SDATA <> io.SDATA
  spi.io.reg <> spi_config
}

object UartTopVerilog extends App {
  Config.spinal.generateVerilog(UartTop())
}
