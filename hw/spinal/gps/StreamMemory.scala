 package gps

import spinal.core._
import spinal.lib._

// TODO: make reads synchronous so BRAM can be used - right now it synthesizes to LUTRAM

case class StreamMemory[T <: Data](dataType: T, sizeLog: Int) extends Component {
  val io = new Bundle {
    val input = slave Stream Fragment(dataType)
    val output = master Stream Fragment(dataType)

    val output_offset = in SInt (sizeLog bits)
  }

  val size = 1 << sizeLog

  io.input.ready := True
  io.output.valid := True

  val mem = Mem(dataType, wordCount = size)
  mem.addAttribute("ram_style", "block")

  val wr_addr = Counter(size, io.input.fire)
  mem.write(wr_addr, io.input.payload, io.input.fire)

  val rd_addr_counter = Counter(size, io.output.fire)
  val rd_addr = (rd_addr_counter.value + io.output_offset.asUInt) % size
  io.output.fragment := mem.readAsync(rd_addr)
  io.output.last := rd_addr_counter.willOverflowIfInc
}

object StreamMemoryVerilog extends App {
  Config.spinal.generateVerilog(StreamMemory(Bits(8 bits), log2Up(16)))
}
