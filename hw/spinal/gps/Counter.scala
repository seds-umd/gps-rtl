package gps

import spinal.core._
import spinal.lib.fsm._
import spinal.lib._

case class Counter() extends Component {
  val io = new Bundle {
    val result = out Bool()
    val counterOut = out UInt(8 bits)
  }

val counter = Reg(UInt(8 bits)) init(0)
    io.result := False
    io.counterOut := counter

 val fsm = new StateMachine {
   
    
    val IDLE: State = new State with EntryPoint {
      whenIsActive(goto(RUN))
    }

    val RUN: State = new State {
      whenIsActive {
        onEntry(counter := 0)
        counter := counter + 1
        when(counter === 15) {
          goto(DONE)
        }
      }
    }

    val DONE: State = new State {
      whenIsActive {
        io.result := True
      }
      
    }
  }
}
object CounterVerilog extends App {
  Config.spinal.generateVerilog(Counter())
}

