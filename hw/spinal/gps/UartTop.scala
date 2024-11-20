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
    val spi = master(SpiBundle())
  }

  val max = MaxInterface(iq_size = 2)
  max.io.max.clk_ser <> io.clk_ser
  max.io.max.data_in <> io.data_in
  max.io.max.data_sync <> io.data_sync
  max.io.max.time_sync <> io.time_sync

  val uart = UartControl(
    iqSize = 2,
    baud = 3125 * 1000,
    memoryBits = 1500 * 1024
  )
  uart.io.uart <> io.uart
  uart.io.iq << max.io.iq.translateInto(Stream(Complex(2)))((to, from) => {
    to := from.c
  })

  val spi = MaxSpiConfig()
  spi.io.spi >> io.spi
  uart.io.spi_data >> spi.io.data
}

object UartTopVerilog extends App {
  Config.spinal.generateVerilog(UartTop())
}
