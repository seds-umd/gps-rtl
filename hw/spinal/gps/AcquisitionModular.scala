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

  def transfer(gateConfig: Stream[UInt], n: Int = 4096) = {
    gateConfig.payload := n
    gateConfig.valid := True
  }

  def conj(stream_in: Stream[Fragment[Complex]]): Stream[Fragment[Complex]] = {
    stream_in.translateInto(stream_in.clone())((to, from) => {
      to.fragment.re := from.fragment.re
      to.fragment.im := -from.fragment.im
      to.last := from.last
    })
  }

  val sample_mem = StreamMemory(Complex(8), fft_size_log)
  val prn_mem = StreamMemory(Complex(8), fft_size_log)

  val prn_gen = PRN()
  prn_gen.io.inc := U"17'h4000" // TODO: automatically calculate based on sample rate
  prn_gen.io.sv := 1
  prn_gen.io.set := False

  val fft = new Area {
    // Get stream without exponent
    def stream_no_exp(stream_in: Axi4Stream): Stream[Fragment[Complex]] = {
      stream_in.translateInto(Stream(Fragment(Complex(fft_width))))((to, from) => {
        to.fragment := from.data.as(Complex(fft_width))
        to.last := from.last
      })
    }

    val inst = XilinxFFT()

    //// Inputs

    // Convert IQ input into 8 bit complex
    val input_gps = io.iq.translateInto(Stream(Complex(8)))((to, from) => {
      val from_iq = from.as(ComplexTimestamp(iq_size, period))
      to.re := from_iq.c.re @@ U"6'b100000"
      to.im := from_iq.c.im @@ U"6'b100000"
    })

    val input_prn = prn_gen.io.code.translateInto(Stream(Complex(8)))((to, from) => {
      // Scale PRN to +-1 (127/-128) and zero imaginary component
      // XOR to convert False to 0x80 (-128) and True to 0x7F (127)
      to.re := from.asSInt.resize(8 bits) ^ S"8'b10000000"
      to.im := 0
    })

    val inputs = Vec(input_gps, input_prn)
    val input_sel = Reg(UInt(log2Up(inputs.length) bits)) init 0

    val INPUT_SEL_GPS = 0
    val INPUT_SEL_PRN = 1

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
    in_gate_config.valid.setAsReg() init(False)

    //// Outputs

    val output_count = 2
    val output_sel = Reg(UInt(log2Up(output_count) bits)) init 0
    val outputs = StreamDemux(inst.io.m_axis_data, output_sel, output_count)

    val OUT_SEL_SAMPLE_MEM = 0
    val OUT_SEL_PRN_MEM = 1

    sample_mem.io.input << conj(stream_no_exp(outputs(OUT_SEL_SAMPLE_MEM)))
    prn_mem.io.input << stream_no_exp(outputs(OUT_SEL_PRN_MEM))

    // FFT config
    val config = inst.io.s_axis_config.clone()
    config >> inst.io.s_axis_config
    config.payload.setAsReg()
    config.valid.setAsReg() init(False)

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

    // Number of active FFT frames, will be 0 or 1 unless using streaming FFT architecture
    val active_frames = CounterUpDown(16, inst.io.s_axis_data.lastFire, inst.io.m_axis_data.lastFire)

    // Active if frames in flight, input gate is running, or input gate is actively being configured
    val input_active = in_gate.io.running || in_gate.io.config.valid
    val output_active = (active_frames > 0)
    val active = input_active || output_active
  }

  val fsm = new StateMachine {
    val init: State = new State with EntryPoint {
      onEntry {
        fft.config.payload := fft.CONFIG_FWD
        fft.config.valid := True

        prn_gen.io.set := True
      }

      whenIsActive {
        goto(samples_in)
      }
    }

    // Grab IQ samples, run FFT and store in memory
    val samples_in: State = new State {
      onEntry {
        fft.input_sel := fft.INPUT_SEL_GPS
        fft.output_sel := fft.OUT_SEL_SAMPLE_MEM
        transfer(fft.in_gate_config)
      }

      whenIsActive {
        when (!fft.input_active) {
          goto(prn_in)
        }
      }
    }

    // Generate PRN samples, run FFT and store in memory
    val prn_in: State = new State {
      onEntry {
        fft.input_sel := fft.INPUT_SEL_PRN
        fft.output_sel := fft.OUT_SEL_PRN_MEM
        transfer(fft.in_gate_config)
      }

      whenIsActive {
        when (!fft.active) {
          goto(shift_mix)
        }
      }
    }

    // Perform frequency search: shift PRN, mix samples and run IFFT
    val shift_mix: State = new State {}
  }
}

object AcquisitionModularVerilog extends App {
  // Generate verilog for testbench. If freq_shift is changed, also change in tb.
  Config.spinal.generateVerilog(AcquisitionModular(freq_shift = 1, flush = false))
}
