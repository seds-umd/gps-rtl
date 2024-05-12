package gps

import spinal.core._
import spinal.lib._
import spinal.lib.bus.amba4.axis.{Axi4Stream, Axi4StreamConfig}

case class MaxMagnitude(iqWidth: Int, freqWidth: Int, fftWidth: Int, axisConfig: Axi4StreamConfig) extends Component {
  val io = new Bundle {
    val input = slave(Axi4Stream(axisConfig))
    val freq = in SInt (freqWidth bits)
    val restart = in Bool ()

    val max_mag = out UInt (iqWidth + 15 bits)
    val max_idx = out UInt (fftWidth bits)
    val max_freq = out SInt (freqWidth bits)
  }

  io.max_mag.setAsReg()
  io.max_idx.setAsReg()
  io.max_freq.setAsReg()

  val mag = MagnitudeStream(iqWidth)
  mag.io.mag.ready := RegNext(!io.restart) init False

  // Convert to normal stream
  mag.io.input << io.input.translateInto(mag.io.input.clone())((to, from) => {
    to.fragment.assignFromBits(from.data)
    to.last := from.last
  })

  // Can assume exponent won't change within a cycle
  val exp = io.input.user.asUInt

  // Saturate exponent to 15 to limit mag_abs width to 8+15
  val mag_abs = mag.io.mag.payload << exp.fixTo(3 downto 0)

  val idx_counter = Counter(fftWidth bits)

  val freq_delayed = Delay(io.freq, LatencyAnalysis(io.input.valid, mag.io.mag.valid), io.input.fire)

  when(mag.io.mag.fire) {
    idx_counter.increment()

    when(mag_abs > io.max_mag) {
      io.max_mag := mag_abs
      io.max_idx := idx_counter
      io.max_freq := freq_delayed
    }
  }

  when(io.restart) {
    io.max_mag := 0
  }
}

object MaxMagnitudeVerilog extends App {
  val axis_config = Axi4StreamConfig(
    dataWidth = 2,
    useLast = true,
    userWidth = 4,
    useUser = true
  )

  Config.spinal.generateVerilog(MaxMagnitude(8, 8, 4, axis_config))
}
