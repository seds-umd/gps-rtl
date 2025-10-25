import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

class VedantMiniProject extends Component {
    val io = new Bundle{
        val counter = out UInt(4 bits) // 4 bits -> counter from 0-15
        val done = out Bool // Output pin signifying program completion
    }

    // Creates register to act as counter with val initialized to 0
    val countReg = Reg(UInt(4 bits)) init(0)

    io.counter := countReg // Wires the value in countReg to counter
    io.done := False // Program's done state defaults to false (0)

    // Creates a 2 bit flip-flop register to handle counting logic
    val fsm = new StateMachine {
        val IDLE, RUN, DONE = new State // Defines potential states
        setEntry(IDLE) // Starts FSM in idle state

        IDLE.whenIsActive {
            countReg := 0 // Starts counter at 0 when in idle state
            goto(RUN) // Begins counting (jumps to run state)
        }

        RUN.whenIsActive {
            when(countReg === 15) { // Jumps to done state when count reaches 15
                goto(DONE)
            } otherwise { // Counts
                countReg := countReg + 1
            }
        }

        DONE.whenIsActive {
            io.done := True // Ends program
        }
    }
}