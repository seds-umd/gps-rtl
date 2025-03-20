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

    val system_clk = in Bool()
    val system_rst = in Bool()
  }

  io.miso := False  

  val systemClockDomain = ClockDomain(
    clock  =  io.system_clk, 
    reset  =  io.system_rst
  )

  val systemArea = new ClockingArea(systemClockDomain) {

    val sclk_sync = BufferCC(io.sclk, False)        // Sync with system clock
    val cs_sync   = BufferCC(io.cs, True) 
    val mosi_sync = BufferCC(io.mosi, False)

    val sclk_prev = RegNext(sclk_sync) init(False)  // Edge detection for SCLK 
    val sclk_rise = sclk_sync && !sclk_prev  
    val sclk_fall = !sclk_sync && sclk_prev 
    
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

      val idle = new State with EntryPoint
      val receiving = new State
      val complete = new State

      idle.whenIsActive {
        when(!cs_sync) {   
          valid_reg := False        
          goto(receiving)
        }
      }

      receiving.whenIsActive {
        when(counter === 16) {
          valid_reg := True
          goto(complete)
        }
      }

      complete.whenIsActive {
        when(cs_sync) {  
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