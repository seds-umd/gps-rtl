package gps

import spinal.core._
import spinal.lib._
import spinal.lib.bus.amba4.axilite.{AxiLite4, AxiLite4Config, AxiLite4SlaveFactory}

case class GpsPeripheral(config: AxiLite4Config) extends Component {
    val io = new Bundle {
        val bus = slave(AxiLite4(config))

        val spi_cs = out Bool()
        val spi_sclk = out Bool()
        val spi_sdata = out Bool()
    }

    val busCtrl = AxiLite4SlaveFactory(io.bus)

    val max_spi = ThreeWireSpi()
    max_spi.io.rst := False
    io.spi_cs := max_spi.io.CS
    io.spi_sclk := max_spi.io.SCLK
    io.spi_sdata := max_spi.io.SDATA

    for (i <- 0 to 7) {
        busCtrl.driveAndRead(max_spi.io.reg(i), 0x4*i)
    }

    // Any write to this reg will trigger SPI config
    busCtrl.onWrite(0x20)(max_spi.io.rst := True)
}

object GpsPeripheralVerilog extends App {
    val config = AxiLite4Config(addressWidth = 12, dataWidth = 32)

    val report = Config.spinal.generateVerilog(GpsPeripheral(config))
    report.printPruned()
}
