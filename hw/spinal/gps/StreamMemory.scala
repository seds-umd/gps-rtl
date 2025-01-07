package gps

import spinal.core._
import spinal.lib._

// Synchronous reads with BRAM

case class StreamMemory[T <: Data](dataType: T, sizeLog: Int) extends Component {
  val io = new Bundle {
    val input = slave Stream Fragment(dataType)
    val output = master Stream Fragment(dataType)

    val output_offset = in SInt (sizeLog bits)
  }

  val size = 1 << sizeLog

  // input always valid
  io.input.ready := True

  val mem = Mem(dataType, wordCount = size)
  mem.addAttribute("ram_style", "block")

  val wr_addr = Counter(size, io.input.fire)
  mem.write(wr_addr, io.input.payload, io.input.fire)

  val rd_addr_counter = Counter(size, io.output.fire)
  val rd_addr = Reg(UInt(sizeLog bits)) init(0)
  val rd_addr_mod = (rd_addr_counter.value + io.output_offset.asUInt) % size

  when(io.output.fire) {
    rd_addr := rd_addr_mod
  }

  val rd_data = mem.readSync(rd_addr, io.output.ready)
  io.output.fragment := rd_data
  io.output.valid := RegNext(io.output.ready, init = False)
  io.output.last := RegNext(rd_addr_counter.willOverflowIfInc, init = False)
}

object StreamMemoryVerilog extends App {
  Config.spinal.generateVerilog(StreamMemory(Bits(8 bits), log2Up(16)))
}