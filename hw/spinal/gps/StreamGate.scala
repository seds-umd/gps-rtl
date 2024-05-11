package gps

import spinal.core._
import spinal.lib._

case class StreamGate[T <: Data](dataType: T, countBits: Int = 13) extends Component {
  val io = new Bundle {
    val input = slave Stream Fragment(dataType)
    val output = master Stream Fragment(dataType)

    val config = slave Stream (UInt(countBits bits))
    val running = out Bool ()
  }

  io.config.ready := True

  val counter = Reg(UInt(countBits bits)) init 0
  io.running := counter > 0

  // Connect input and output
  io.output << io.input.haltWhen(!io.running)

  // Set counter from config
  when(io.config.fire) {
    counter := io.config.payload
  }

  // Count transfers
  when(io.running && io.output.fire) {
    counter := counter - 1
  }
}
