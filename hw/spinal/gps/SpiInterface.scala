package gps
import spinal.core._
import spinal.lib._
import spinal.lib.fsm._



case class SpiInterface() extends Component {
  val io = new Bundle {
    val sclk = in Bool()
    val mosi = in Bool()
    val cs = in Bool()
    val reset = in Bool()
    val cmd_test = out UInt(16 bits)
  }

  // Create SPI clock domain
  val spiClockDomain = ClockDomain(
    clock = io.sclk,
    reset = io.reset,
    config = ClockDomainConfig(
      clockEdge = RISING,
      resetKind = ASYNC,
      resetActiveLevel = HIGH
    )
  )

  val zeroReg = Reg(UInt(16 bits)) init(0)
  io.cmd_test := zeroReg


  val spiArea = new ClockingArea(spiClockDomain) {
    val cmdReg = Reg(UInt(16 bits)) init(0)
    val counter = Reg(UInt(5 bits)) init(0)
    val mosiReg = Reg(UInt(16 bits)) init(0)


    when(io.cs === False){
      counter := counter + 1
      mosiReg := (mosiReg |<< 1) + io.mosi.asUInt

      when(counter === 16){
        counter:=0
        cmdReg := mosiReg
      }
    }

  }



}



object SpiInterfaceVerilog extends App {
  Config.spinal.generateVerilog(SpiInterface())
}
