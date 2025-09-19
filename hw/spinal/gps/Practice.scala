package gps

import spinal.core._
import spinal.lib._

// fsm or smth else related to spi
// logic analyzer?

case class Practice() extends Component {

    val io = new Bundle {
       val output = out UInt(4 bits)
    }

    val counter = Reg(UInt(4 bits)) init(0)   

    counter := counter + 1    // Sequential
    io.output := counter     // Combinational
}

object PracticeVerilog extends App {
  Config.spinal.generateVerilog(Practice())
}


/* 
case class Practice() extends Component {
  val io = new Bundle {
    val output = out UInt(4 bits)
    val done   = out Bool()
  }

  val counter = Reg(UInt(4 bits)) init(0)

  val fsm = new StateMachine {
    val IDLE = new State with EntryPoint
    val RUN  = new State
    val DONE = new State

    io.output := counter
    io.done := False

    IDLE.whenIsActive {
      counter := 0
      goto(RUN)
    }

    RUN.whenIsActive {
      counter := counter + 1
      when(counter === 15) {
        goto(DONE)
      }
    }

    DONE.whenIsActive {
      io.done := True
    }
  }
}
 */