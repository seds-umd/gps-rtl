package gps

import spinal.core._
import spinal.lib._

class StreamDemuxMetered[T <: Data](input: Stream[T], ports: Int, countBits: Int = 12) extends Area {
  private val select = Stream(UInt(log2Up(ports) bits))
  select.payload.setAsReg()
  select.valid.setAsReg()

  private val counter = Reg(UInt(countBits bits)) init 0
  private val target = Reg(UInt(countBits bits))
  private val running = counter > 0

  private val input_internal = input.haltWhen(!running || select.valid)
  // val outputs = StreamDemux(input_internal, select, ports)
  val outputs = Vec(input_internal) // XXX just to get it to compile, fix later

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
  when(running && !select.valid && input.fire) {
    counter := counter - 1
  }
}

case class StreamDemuxMeteredTest() extends Component {
  val io = new Bundle {
    val input = slave Stream (Bits(8 bits))
    val outputs = Vec(master Stream (Bits(8 bits)), 4)

    val sel = in UInt (2 bits)
    val run = in Bool ()
  }

  val mux = new StreamDemuxMetered(io.input, 4)
  (mux.outputs, io.outputs).zipped.map(_ >> _)

  when(io.run && !mux.busy()) {
    mux.transfer(io.sel, 8)
  }
}

object StreamDemuxMeteredVerilog extends App {
  Config.spinal.generateVerilog(StreamDemuxMeteredTest())
}
