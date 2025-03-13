package gps

import spinal.core._
import spinal.lib._

case class SpiSlave() extends Component {
  val io = new Bundle {
    val cs       =   in Bool()
    val sclk     =   in Bool()
    val tx       =   in Bool()
    val rx       =   out Bool()

    val is_valid =   out Bool()
    val is_read  =   out Bool()    // read = 1 write = 0
    val cmd      =   out Bits(16)
    val addr     =   out Bits(16)
  }

  val valid_reg = Reg(Bool()) init(False)
  val input_reg = Reg(Bits(16 bits)) init(0)
  val cmd_reg = Reg(Bits(16 bits)) init(0)
  val addr_reg = Reg(Bits(16 bits)) init(0)
  val counter = Reg(UInt(4 bits)) init(0)    // (2 byte cmd/addr)

  val fsm = new StateMachine() {

    val idle: State = new State with EntryPoint {
      whenIsActive {
        valid_reg := False
        counter := 0

        when(!io.cs) {     // active-low
          input_reg := 0
          goto(receive_command)
        }
      }
    }

    val receive_command: State = new State {
      whenIsActive {
        when(io.spi_cs) { 
          goto(idle)

        } otherwise {
          when(io.sclk.rise) {
            input_reg := (input_reg(14 down to 0) ## B(io.tx))
            counter := counter + 1

            when (counter === 15) {
              cmd_reg := input_reg
              counter := 0
              goto(receive_address)
            }
          }
        }  
      }
    }

    val receive_address: State = new State {
      whenIsActive {
        when(io.spi_cs) { 
          goto(idle)

        } otherwise {
          when(io.sclk.rise) {
            input_reg := (input_reg(14 down to 0) ## B(io.tx))
            counter := counter + 1

            when (counter === 15) {
              addr_reg := input_reg
              valid_reg := True
              goto(finish)
            }
          }
        }
      }
    }

    val finish: State = new State {
      whenIsActive {
        // valid_reg := False    ?
        when(io.cs) {
          goto(idle)
        }
      }
    }
  }

  io.is_valid   := valid_reg
  io.is_read    := cmd_reg(15) 
  io.cmd        := cmd_reg
  io.addr       := addr_reg
}

object SpiSlaveVerilog extends App {
  Config.spinal.generateVerilog(SpiSlave())
}
