package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

case class SpiSlave() extends Component {
  val io = new Bundle {
    val cs     =   in Bool()    
    val sclk   =   in Bool()    
    val mosi   =   in Bool()    
    val miso   =   out Bool()  

    val received_bit = out Bool()  
  }

  io.miso := False  

  val SpiClockDomain = ClockDomain(
    clock = io.sclk,
    config = ClockDomainConfig(
      resetKind = BOOT,
      clockEdge = FALLING         // SPI Mode 1
    )
  )

  val SpiArea = new ClockingArea(SpiClockDomain) {
    
    val received_reg = Reg(Bool()) init(False)

    when(!io.cs) {                // active-low
      received_reg := io.mosi  
    }

    io.received_bit := received_reg 
  }
}

object SpiSlaveVerilog extends App {
  Config.spinal.generateVerilog(SpiSlave())
}