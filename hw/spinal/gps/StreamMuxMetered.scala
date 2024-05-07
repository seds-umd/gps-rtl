package gps

import spinal.core._
import spinal.lib._

class StreamMuxMetered[T <: Data](inputs: Vec[Stream[T]], countBits: Int = 12) extends Area {
  private val select = Stream(UInt(log2Up(inputs.length) bits))
  select.payload.setAsReg()
  select.valid.setAsReg()

  private val counter = Reg(UInt(countBits bits)) init 0
  private val target = Reg(UInt(countBits bits))
  private val running = counter > 0

  private val inputs_internal = Vec(inputs.map(_.haltWhen(!running || select.valid)))
  val output = StreamMux(select, inputs_internal)

  // Perform n transactions to bus at index
  // Only run when not busy
  def transfer(index: UInt, n: Int) = {
    counter := n

    select.payload := index
    select.valid := True
  }

  // Check if busy
  def busy(): Bool = {
    return running
  }

  // Check remaining
  def remaining(): UInt = {
    return counter
  }

  // Handle select
  when(select.fire) {
    select.valid := False
  }

  // Count each transaction after selection is done
  when(running && !select.valid && output.fire) {
    counter := counter - 1
  }
}

case class StreamMuxMeteredTest() extends Component {
  val io = new Bundle {
    val inputs = Vec(slave Stream (Bits(8 bits)), 4)
    val output = master Stream (Bits(8 bits))

    val sel = in UInt (2 bits)
    val run = in Bool ()
  }

  val mux = new StreamMuxMetered(io.inputs)
  mux.output >> io.output

  when(io.run && !mux.busy()) {
    mux.transfer(io.sel, 8)
  }
}

object StreamMuxMeteredVerilog extends App {
  Config.spinal.generateVerilog(StreamMuxMeteredTest())
}
