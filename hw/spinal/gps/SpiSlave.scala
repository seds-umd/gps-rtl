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

  val sclk_sync = BufferCC(io.sclk, False)        // Sync with system clock
  val cs_sync   = BufferCC(io.cs, True) 
  val mosi_sync = BufferCC(io.mosi, False)

  val sclk_rise = sclk_sync.rise(False)         
  val sclk_fall = sclk_sync.fall(False)
  
  val shift_reg = Reg(Bits(16 bits)) init(0) 
  val counter   = Reg(UInt(5 bits)) init(0)    
  val valid_reg = Reg(Bool()) init(False)

  when(!cs_sync) { 
    when (sclk_fall) {                            // SPI Mode 1
      shift_reg := shift_reg(14 downto 0) ## mosi_sync
      counter := counter + 1
    }
  }.otherwise {
    counter := 0
  }

  val fsm = new StateMachine {

    val idle : State = new State with EntryPoint {
      whenIsActive {
        when(!cs_sync) {   
          valid_reg := False        
          goto(receiving)
        }
      }
    }

    val receiving : State = new State {
      whenIsActive {
        when(counter === 16) {                    // Delay bc of CDC
          valid_reg := True
          goto(complete)
        }
      }
    }

    val complete : State = new State {
      whenIsActive {
        when(cs_sync) {  
          goto(idle)
        }
      }
    }
  }

  io.rw := shift_reg(15) 
  io.addr := shift_reg(14 downto 0) 
  io.received_flag := valid_reg
}

object SpiSlaveVerilog extends App {
  Config.spinal.generateVerilog(SpiSlave())
}