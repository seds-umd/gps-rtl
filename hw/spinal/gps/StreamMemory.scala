package gps

import spinal.core._
import spinal.lib._

// Synchronous reads with BRAM

case class StreamMemory[T <: Data](dataType: T, sizeLog: Int) extends Component {
  val io = new Bundle {
    val input = slave Stream Fragment(dataType)
    val output = master Stream Fragment(dataType)

    val run = in Bool ()
    val output_offset = in SInt (sizeLog bits)
  }

  val size = 1 << sizeLog

  io.input.ready := True

  val mem = Mem(dataType, wordCount = size)
  mem.addAttribute("ram_style", "block")

  val wr_addr = Counter(size, io.input.fire)
  mem.write(wr_addr, io.input.payload, io.input.fire)

  val pre_gate = Stream(io.output.payload.clone)

  val rd_addr_counter = Counter(size)
  val rd_addr = (rd_addr_counter.valueNext + io.output_offset.asUInt) % size
  pre_gate.fragment := mem.readSync(rd_addr.resized)
  pre_gate.last := rd_addr_counter.willOverflowIfInc
  pre_gate.valid := True

  when(pre_gate.fire) {
    rd_addr_counter.increment()
  }

  val gate = StreamGate(pre_gate.payload.clone)
  gate.io.input << pre_gate
  io.output << gate.io.output

  gate.io.config.payload := 1 << sizeLog
  gate.io.config.valid := io.run.rise
}

object StreamMemoryVerilog extends App {
  Config.spinal.generateVerilog(StreamMemory(Bits(8 bits), log2Up(16)))
}
