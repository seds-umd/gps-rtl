package gps

import spinal.core._
import spinal.lib._

class StreamDemuxMetered[T <: Data](input: Stream[T], ports: Int, countBits: Int = 12) extends Area {
  private val select = Reg(UInt(log2Up(ports) bits)) init 0

  private val counter = Reg(UInt(countBits bits)) init 0
  private val running = counter > 0

  private val input_internal = input.haltWhen(!running)
  val outputs = StreamDemux(input_internal, select, ports)

  // Perform n transactions to bus at index
  // Only run when not busy
  def transfer(index: UInt, n: Int) = {
    counter := n

    select := index
  }

  // Check if busy
  def busy(): Bool = {
    return running
  }

  // Check remaining
  def remaining(): UInt = {
    return counter
  }

  // Count only accepted transfers; selection stays fixed for the burst
  when(running && input.fire) {
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
