package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.bus.amba4.axis.Axi4Stream.Axi4Stream

case class AcquisitionModular(
    iq_size: Int = 2,
    fft_size: Int = 4096,
    fft_width: Int = 8,
    freq_shift: Int = 24,
    dec_factor: Int = 8,
    period: Int = 4092,
    flush: Boolean = true
) extends Component {
  val fft_size_log = log2Up(fft_size)

  val io = new Bundle {
    val iq = slave Stream (ComplexTimestamp(iq_size, period).asBits)
  }

  def transfer[T <: Data](gateConfig: Stream[UInt], n: Int = 4096) = {
    gateConfig.payload := n
    gateConfig.valid := True
  }

  val fft = new Area {
    // Get stream without exponent
    def stream_no_exp(stream_in: Axi4Stream): Stream[Fragment[Complex]] = {
      val stream_out = Stream(Fragment(Complex(fft_width)))

      stream_out.ready <> stream_in.ready
      stream_out.valid <> stream_in.valid
      stream_out.last <> stream_in.last
      stream_out.fragment <> stream_in.data.as(Complex(fft_width))
      stream_out
    }

    val inst = XilinxFFT()

    // Inputs

    // Convert IQ input into 8 bit complex
    val input_gps = io.iq.translateInto(Stream(Complex(8)))((to, from) => {
      val from_iq = from.as(ComplexTimestamp(iq_size, period))
      to.re := from_iq.c.re @@ U"6'b100000"
      to.im := from_iq.c.im @@ U"6'b100000"
    })

    val inputs = Vec(input_gps)
    val input_sel = Reg(UInt(log2Up(inputs.length) bits))

    // Input gate
    val in_gate = StreamToFragmentMetered(inst.io.s_axis_data.dataType)
    in_gate.io.output >> inst.io.s_axis_data
    in_gate.io.input << StreamMux(input_sel, inputs).translateInto(Stream(Bits(16 bits)))((to, from) => {
      to := from.asBits
    })

    // Gate configuration
    val in_gate_config = in_gate.io.config.clone()
    in_gate_config >> in_gate.io.config
    in_gate_config.payload.setAsReg()
    in_gate_config.valid.setAsReg()

    // Outputs
    val output_count = 0
    val output_sel = Reg(UInt(log2Up(output_count) bits))
    val outputs = StreamDemux(inst.io.m_axis_data, output_sel, output_count)

    // FFT config
    val config = inst.io.s_axis_config.clone()
    config >> inst.io.s_axis_config
    config.valid.setAsReg()
    config.payload.setAsReg()

    val CONFIG_FWD = 1
    val CONFIG_REV = 0

    // FFT status - ignore
    inst.io.m_axis_status.ready := True

    // Reset all config buses after a cycle
    when(config.fire) {
      config.valid := False
    }

    when(in_gate_config.fire) {
      in_gate_config.valid := False
    }
  }

  val fsm = new StateMachine {
    val init: State = new State with EntryPoint {
      onStart {
        fft.config.payload := fft.CONFIG_FWD
        fft.config.valid := True
      }

      whenIsActive {
        goto(samples_in)
      }
    }

    val samples_in: State = new State {
      onStart {
        fft.input_sel := 0
        transfer(fft.in_gate_config)
      }

      whenIsActive {
        // when (!fft.in_gate.busy()) {
        //   goto()
        // }
      }
    }
  }
}

object AcquisitionModularVerilog extends App {
  // Generate verilog for testbench. If freq_shift is changed, also change in tb.
  Config.spinal.generateVerilog(AcquisitionModular(freq_shift = 1, flush = false))
}
