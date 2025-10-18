import spinal.core._
import spinal.lib._

class VedantMiniProject extends Component {
    val io = new Bundle{
        val done = out Bool // Output pin signifying program completion
        val counter = out UInt(4 bits) // 4 bits -> counter from 0-15
    }

    // Creates register to hold counter with reset val initialized to 0
    val countReg = Reg(UInt(4 bits)) init(0)

    io.counter := countReg // Wires the current value in countReg to counter
    
}