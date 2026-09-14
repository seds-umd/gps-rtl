package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.bus.amba4.axis.Axi4Stream.Axi4Stream

/** TODO:
  * sample phase isn't constant between runs - is this due to changes in sim data or bug in rtl?
  * only detecting 5 SVs at best when python code is detecting 8
  */

/** Potential improvements:
  * Skip SVs that are already in tracking channels
  * Skip fine acquisition if coarse acquisition SNR isn't high enough - maybe a bad idea of it's right on the edge of the threshold, and fine acquisition would reveal a higher SNR
  */

case class AcquisitionResults(fft_size_log: Int = 12) extends Bundle {
  // SV is 1 indexed (0 is never used)
  val sv = UInt(6 bits)

  // Fine acquisition frequency (scaled by 1/dec_factor)
  val freq_offset = SInt(fft_size_log bits)

  // Phase offset in samples (out of 4092)
  val phase_offset = UInt(fft_size_log bits)

  // Integer portion of SNR based on fine acquisition results
  val snr = UInt(8 bits)
}

case class AcquisitionModular(
    iq_size: Int = 2,
    fft_size: Int = 4096,
    fft_width: Int = 8,
    freq_shift: Int = 24,
    dec_factor: Int = 8,
    period: Int = 4092,
    flush: Boolean = true,
    debug: Boolean = false
) extends Component {
  val fft_size_log = log2Up(fft_size)
  val freq_width = log2Up(2 * freq_shift + 1)

  val io = new Bundle {
    val iq = slave Stream (ComplexTimestamp(iq_size, period).asBits)
    val results = master Stream (AcquisitionResults(fft_size_log))
    // Input window state, independent of iq.valid/ready. Live front ends may
    // drain samples between windows but must preserve them during a window.
    val capture_active = out Bool ()
  }

  printf("IQ total width: %d\n", io.iq.payload.getWidth)

  io.results.sv := 0
  io.results.freq_offset := 0
  io.results.phase_offset := 0
  io.results.snr := 0
  io.results.valid := False

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

  def shift_sat(stream_in: Stream[Fragment[Complex]], shift: Int): Stream[Fragment[Complex]] = {
    stream_in.translateInto(stream_in.clone())((to, from) => {
      to.fragment.re := (from.fragment.re << shift).sat(shift bits)
      to.fragment.im := (from.fragment.im << shift).sat(shift bits)
      to.last := from.last
    })
  }

  def scale4096_4092(value: UInt): UInt = {
    val scaled = UInt(fft_size_log bits)
    when(value < 4092 * 1 / 5) {
      scaled := value
    } elsewhen (value < 4092 * 2 / 5) {
      scaled := value - 1
    } elsewhen (value < 4092 * 3 / 5) {
      scaled := value - 2
    } elsewhen (value < 4092 * 4 / 5) {
      scaled := value - 3
    } otherwise {
      scaled := value - 4
    }
    scaled
  }

  val iq_area = new Area {
    val iq_converted = io.iq.translateInto(Stream(ComplexTimestamp(iq_size)))((to, from) => {
      to.assignFromBits(from)
    })
    val output_count = 2
    val output_sel = Reg(UInt(log2Up(output_count) bits)) init 0
    val outputs = StreamDemux(iq_converted, output_sel, output_count)

    val OUT_SEL_COARSE = 0
    val OUT_SEL_FINE = 1

    val output_coarse = outputs(OUT_SEL_COARSE)
    val output_fine = outputs(OUT_SEL_FINE)
  }

  // Memories
  val sample_mem = StreamMemory(Complex(8), fft_size_log)
  sample_mem.io.output_offset := 0
  val prn_mem = StreamMemory(Complex(8), fft_size_log)

  // PRN
  val prn_gen = Prn()
  prn_gen.io.inc := U"17'h4000" // TODO: automatically calculate based on sample rate
  prn_gen.io.set := False

  val sv = Reg(UInt(6 bits)) init 0
  prn_gen.io.sv := sv

  // Feed sample and PRN memory into mixer
  val mixer = Mixer(8)
  mixer.io.input_a << sample_mem.io.output
  mixer.io.input_b << prn_mem.io.output

  val fine_acq = new Area {
    val remove_prn = RemovePrn(iq_size, fft_width, period, fft_size_log, 4.092 MHz, debug)
    remove_prn.io.sv := sv
    remove_prn.io.set := False
    remove_prn.io.input << iq_area.output_fine

    val decimator = Decimate(iq_in_size = fft_width, iq_out_size = fft_width, factor = dec_factor)
    decimator.io.iq_in << remove_prn.io.output
    val dec_out = decimator.io.iq_out
  }

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
    val input_gps = iq_area.output_coarse.translateInto(Stream(Complex(8)))((to, from) => {
      to.re := from.c.re @@ U"6'b100000"
      to.im := from.c.im @@ U"6'b100000"
    })
    val input_gps_time = io.iq.payload.as(ComplexTimestamp(iq_size, period)).t

    val input_prn = prn_gen.io.code.translateInto(Stream(Complex(8)))((to, from) => {
      // Scale PRN to +-1 (127/-128) and zero imaginary component
      // XOR to convert False to 0x80 (-128) and True to 0x7F (127)
      to.re := from.asSInt.resize(8 bits) ^ S"8'b10000000"
      to.im := 0
    })

    val input_mixed = mixer.io.output.toStreamOfFragment

    val input_dec = fine_acq.dec_out

    val inputs = Vec(input_gps, input_prn, input_mixed, input_dec)
    val input_sel = Reg(UInt(log2Up(inputs.length) bits)) init 0

    val INPUT_SEL_GPS = 0
    val INPUT_SEL_PRN = 1
    val INPUT_SEL_MIX = 2
    val INPUT_SEL_DEC = 3

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
    in_gate_config.valid.setAsReg() init (False)

    //// Outputs

    val output_count = 3
    val output_sel = Reg(UInt(log2Up(output_count) bits)) init 0
    val outputs = StreamDemux(inst.io.m_axis_data, output_sel, output_count)

    val OUT_SEL_SAMPLE_MEM = 0
    val OUT_SEL_PRN_MEM = 1
    val OUT_SEL_MAG = 2

    // Shift bits to get more dynamic range and saturate
    sample_mem.io.input << shift_sat(conj(stream_no_exp(outputs(OUT_SEL_SAMPLE_MEM))), 2)
    prn_mem.io.input << shift_sat(stream_no_exp(outputs(OUT_SEL_PRN_MEM)), 1)
    val out_mag = outputs(OUT_SEL_MAG)

    // FFT config
    val config = inst.io.s_axis_config.clone()
    config >> inst.io.s_axis_config
    config.payload.setAsReg()
    config.valid.setAsReg() init (False)

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

  io.capture_active := fft.input_active &&
    ((fft.input_sel === fft.INPUT_SEL_GPS) || (fft.input_sel === fft.INPUT_SEL_DEC))

  val shift = Reg(SInt(freq_width bits))
  prn_mem.io.output_offset := (-shift).resized

  // Magnitude
  val max_mag = MaxMagnitude(fft_width, freq_width, fft_size_log, fft.inst.data_out_config)
  max_mag.io.input << fft.out_mag
  max_mag.io.freq <> shift
  max_mag.io.restart := False

  val first_sample_time = Reg(UInt(log2Up(period) bits))
  val phase_offset = Reg(UInt(fft_size_log bits))
  val coarse_freq = Reg(SInt(freq_width bits))
  val fine_freq = Reg(SInt(fft_size_log bits))
  val fine_mean = Reg(UInt(max_mag.io.mean_mag.getBitsWidth bits))
  val fine_max = Reg(UInt(max_mag.io.max_mag.getBitsWidth bits))
  fine_acq.remove_prn.io.phase_offset := phase_offset

  val snr = Snr(fine_mean.getBitsWidth)
  val snr_start = Reg(Bool())
  val snr_result = Reg(UInt(8 bits))
  snr.io.num := fine_max.resized
  snr.io.den := fine_mean
  snr_start := False
  snr.io.start := snr_start

  val fsm = new StateMachine {
    val init: State = new State with EntryPoint {
      onEntry {
        fft.config.payload := fft.CONFIG_FWD
        fft.config.valid := True

        shift := -freq_shift

        max_mag.io.restart := True
      }

      whenIsActive {
        prn_gen.io.set := True

        goto(samples_in)
      }
    }

    // Grab IQ samples, run FFT and store in memory
    val samples_in: State = new State {
      onEntry {
        iq_area.output_sel := iq_area.OUT_SEL_COARSE
        fft.input_sel := fft.INPUT_SEL_GPS
        fft.output_sel := fft.OUT_SEL_SAMPLE_MEM
        transfer(fft.in_gate_config)
      }

      whenIsActive {
        when(fft.in_gate.io.output.firstFire) {
          first_sample_time := fft.input_gps_time
        }
        when(!fft.active) {
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
        when(!fft.active) {
          goto(shift_mix)
        }
      }
    }

    // Perform frequency search: shift PRN, mix samples and run IFFT
    val shift_mix: State = new State {
      onEntry {
        fft.config.payload := fft.CONFIG_REV
        fft.config.valid := True

        fft.input_sel := fft.INPUT_SEL_MIX
        fft.output_sel := fft.OUT_SEL_MAG

        transfer(fft.in_gate_config)
      }

      whenIsActive {
        when(!fft.active & max_mag.io.done_last) {
          when(shift === freq_shift) {
            goto(evaluate)
          } otherwise {
            goto(do_shift)
          }
        }
      }
    }

    // Shift frequency and search again. This doesn't need to be a separate state
    // but it was the easiest solution and I was lazy
    val do_shift: State = new State {
      whenIsActive {
        shift := shift + 1
        goto(shift_mix)
      }
    }

    // Take magnitude of FFT output and keep track of max
    val evaluate: State = new State {
      whenIsActive {
        // Convert FFT phase before applying the timestamp origin: the FFT
        // wraps at4096, but the C/A sample epoch wraps at4092.
        val relative_phase = scale4096_4092(max_mag.io.max_idx)
        val absolute_phase = relative_phase.resize(fft_size_log + 1) + period - first_sample_time.resize(fft_size_log + 1)
        phase_offset := Mux(absolute_phase >= period, absolute_phase - period, absolute_phase).resized
        coarse_freq := max_mag.io.max_freq
        goto(fine_setup)
      }
    }

    val fine_setup: State = new State {
      whenIsActive {
        fft.config.payload := fft.CONFIG_FWD
        fft.config.valid := True

        iq_area.output_sel := iq_area.OUT_SEL_FINE
        fft.input_sel := fft.INPUT_SEL_DEC
        fft.output_sel := fft.OUT_SEL_MAG

        max_mag.io.restart := True

        goto(fine_run)
      }
    }

    val fine_run: State = new State {
      onEntry {
        transfer(fft.in_gate_config)

        fine_acq.remove_prn.io.set := True
      }

      whenIsActive {
        when(!fft.active & max_mag.io.done_last) {
          goto(fine_eval)
        }
      }
    }

    val fine_eval: State = new State {
      whenIsActive {
        fine_freq := max_mag.io.max_idx.asSInt
        fine_mean := max_mag.io.mean_mag
        fine_max := max_mag.io.max_mag
        snr_start := True

        goto(calc_snr)
      }
    }

    // Delay to allow SNR divider to start
    val calc_snr: State = new StateDelay(cyclesCount = 2) {
      whenCompleted {
        when(snr.io.valid) {
          // Saturate to 255 max
          snr_result := snr.io.res.sat(snr.io.res.getBitsWidth - 8 bits)

          goto(send_result)
        } elsewhen (snr.io.error) {
          snr_result := 0

          goto(send_result)
        }
      }
    }

    val send_result: State = new State {
      whenIsActive {
        io.results.sv := sv + 1
        io.results.freq_offset := fine_freq
        io.results.phase_offset := phase_offset
        io.results.snr := snr_result
        io.results.valid := True

        when(io.results.fire) {
          when(sv === 31) {
            sv := 0
          } otherwise {
            sv := sv + 1
          }

          goto(init)
        }
      }
    }
  }
}

object AcquisitionModularVerilog extends App {
  // Generate verilog for testbench. If freq_shift is changed, also change in tb.
  Config.spinal.generateVerilog(AcquisitionModular(freq_shift = 2, flush = false, debug = true))
}
