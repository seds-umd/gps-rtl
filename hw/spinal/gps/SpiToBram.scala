package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.bus.bram._

/* 
Receives SPI (Mode 1) commands:
- 16-bit command word [bit15 = R/W, bits14..0 = address]
- On read, waits 1-byte gap, then shifts out the read result from BRAM
- On write, 

Exposes a BRAM master interface 
- dataWidth=16, addressWidth=15
*/

case class SpiToBram() extends Component {
  val io = new Bundle {
    val cs     =   in Bool()    
    val sclk   =   in Bool()    
    val mosi   =   in Bool()    
    val miso   =   out Bool()  

    val bram = master(BRAM(BRAMConfig(
      dataWidth    = 16,
      addressWidth = 15,
      readLatency  = 1
    )))
  }

  io.bram.en     := False
  io.bram.we     := 0
  io.bram.addr   := 0
  io.bram.wrdata := 0

  val sclk_sync = BufferCC(io.sclk, False)        // Sync with system clock
  val cs_sync   = BufferCC(io.cs, True) 
  val mosi_sync = BufferCC(io.mosi, False)

  val sclk_rise = sclk_sync.rise(False)         
  val sclk_fall = sclk_sync.fall(False)
  
  val shift_reg_rx = Reg(Bits(16 bits)) init(0)
  val shift_reg_tx = Reg(Bits(16 bits)) init(0)   // Slave (FPGA) is transmitting data on MISO

  val rx_counter = Reg(UInt(6 bits)) init(0)
  val tx_counter = Reg(UInt(6 bits)) init(0)     

  val rx_enable = Reg(Bool()) init(False)
  val tx_enable = Reg(Bool()) init(False)

  io.miso := (tx_enable ? shift_reg_tx(15) | False)

  when(!cs_sync) {
    when(sclk_fall && rx_enable) {
      shift_reg_rx := shift_reg_rx(14 downto 0) ## mosi_sync
      rx_counter := rx_counter + 1
    }
    
    when(sclk_rise && tx_enable) {                // Shift out on rising edge
      shift_reg_tx:= shift_reg_tx(14 downto 0) ## B"0"
      tx_counter := tx_counter + 1
    }
  } otherwise {
    rx_counter  := 0
    tx_counter  := 0
  }

  val rw   = shift_reg_rx(15)                       // 1 -> read, 0 -> write
  val addr = shift_reg_tx(14 downto 0).asUInt       // 15 bits of address

  val fsm = new StateMachine {
    tx_enable := False
    rx_enable := False

    val idle : State = new State with EntryPoint {
      whenIsActive {
        when(!cs_sync) {
          rx_enable := True
          goto(receive_command)
        }
      }
    }

    val receive_command : State = new State {
      whenIsActive {
        rx_enable := True
        when(rx_counter === 16) {
          rx_enable := False
          when(rw) {
            io.bram.en   := True
            io.bram.we   := 0
            io.bram.addr := addr
            goto(gap_byte)
          } otherwise {
            // TODO: implement write path
            goto(complete)
          }
        }
      }
    }

    val gap_byte : State = new State {
      whenIsActive {
        rx_enable := True
        when(rx_counter === 24) {
          rx_enable := False
          shift_reg_tx := io.bram.rddata
          goto(shift_out)
        }
      }
    }

    val shift_out : State = new State {
      whenIsActive {
        tx_enable := True
        when(tx_counter === 16) {
          tx_enable := False
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
}

object SpiToBramVerilog extends App {
  Config.spinal.generateVerilog(SpiToBram())
}