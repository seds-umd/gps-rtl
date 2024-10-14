package gps

import spinal.core._
import spinal.lib._

case class StreamGate[T <: Data](dataType: T, countBits: Int = 13, fragment: Boolean = true) extends Component {
  // Optional fragment or normal stream
  if (fragment) {
    val _dataType = Fragment(dataType)
  } else {
    val _dataType = dataType
  }

  val io = new Bundle {
    val input = slave Stream (dataType)
    val output = master Stream (dataType)

    val config = slave Flow (UInt(countBits bits))
    val running = out Bool ()
  }

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
