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

    val rw             = out Bool()  
    val addr           = out Bits(15 bits) 
    val received_flag  = out Bool()  
  }

  io.miso := False  

  val SpiClockDomain = ClockDomain(
    clock = io.sclk,
    config = ClockDomainConfig(
      resetKind = BOOT,
      clockEdge = FALLING         // SPI Mode 1 : CPOL=0, CPHA=1
    )
  )

  val SpiArea = new ClockingArea(SpiClockDomain) {

    val shift_reg = Reg(Bits(16 bits)) init(0) 
    val counter   = Reg(UInt(5 bits)) init(0)     // max 16
    val valid_reg = Reg(Bool()) init(False)

    when(!io.cs) { 
      shift_reg := shift_reg(14 downto 0) ## io.mosi  
      counter := counter + 1
    }.otherwise {
      counter := 0
      valid_reg := False
    }

    val fsm = new StateMachine {

      val idle = new State with EntryPoint
      val receiving = new State
      val complete = new State

      idle.whenIsActive {
        valid_reg := False

        when(!io.cs) {            // active-low
          goto(receiving)
        }
      }

      receiving.whenIsActive {
        when(counter === 15) {
          valid_reg := True
          goto(complete)
        }
      }

      complete.whenIsActive {
        when(io.cs) {  
          goto(idle)
        }
      }
    }

    io.rw := shift_reg(15) 
    io.addr := shift_reg(14 downto 0) 
    io.received_flag := valid_reg
  }
}

object SpiSlaveVerilog extends App {
  Config.spinal.generateVerilog(SpiSlave())
}