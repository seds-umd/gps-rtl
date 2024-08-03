package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

/* TODO
 * Handle FFT aresetn and aclken
 */

case class Acquisition(
    iq_size: Int = 2,
    fft_size: Int = 4096,
    fft_width: Int = 8,
    freq_shift: Int = 24, // Increasing this number makes the code ITAR
    dec_factor: Int = 8,
    period: Int = 4092,
    flush: Boolean = true
) extends Component {
  val fft_size_log = log2Up(fft_size)

  val io = new Bundle {
    val iq = slave Stream (ComplexTimestamp(iq_size, period).asBits)

    val temp_fft_index = out UInt (fft_size_log bits)
    val temp_fft_val = out UInt (23 bits)
  }

  io.iq.ready := False

  // Convert from 4092 to 4096 as linearly as possible
  def to4096(x: UInt): UInt = x + ((x +^ 512) >> 10)

  val sample_mem = Mem(Complex(fft_width).asBits, wordCount = fft_size)
  val prn_mem = Mem(Complex(fft_width).asBits, wordCount = fft_size)
  sample_mem.addAttribute("ram_style", "block")
  prn_mem.addAttribute("ram_style", "block")

  val fft = new Area {
    val inst = XilinxFFT()

    val config_valid = Reg(Bool()) init False
    val config_payload = Reg(Bits(8 bits)) init 0

    inst.io.s_axis_config.valid <> config_valid
    inst.io.s_axis_config.payload <> config_payload

    val data_in_valid = Reg(Bool()) init False
    val data_in_payload = Reg(Bits(16 bits)) init 0
    val data_in_last = Reg(Bool()) init False

    inst.io.s_axis_data.valid <> data_in_valid
    inst.io.s_axis_data.payload <> data_in_payload
    inst.io.s_axis_data.last <> data_in_last

    val data_out_ready = Reg(Bool()) init False
    inst.io.m_axis_data.ready <> data_out_ready

    // val status_ready = Reg(Bool()) init True
    // inst.io.m_axis_status.ready <> status_ready
    inst.io.m_axis_status.ready := True // Don't need status stream
  }

  // Used for initial acquisition
  val prn1 = Prn()
  val prn1_ready = Reg(Bool()) init False
  prn1.io.inc := U"17'h4000" // TODO: automatically calculate based on sample rate
  prn1.io.set := False
  prn1.io.code.ready := prn1_ready

  // Used for code removal in fine acquisition
  val prn2 = Prn()
  prn2.io.inc := U"17'h4000"
  prn2.io.set := False
  prn2.io.code.ready := False

  val iq_complex = io.iq.payload.as(ComplexTimestamp(iq_size, period))

  val fsm = new StateMachine {
    val sample_counter = Counter(fft_size_log + 1 bits) // TODO: better to split this up for each state?

    val sv = Reg(UInt(6 bits)) init 0
    val shift = Reg(SInt(log2Up(freq_shift * 2 + 1) bits)) init -freq_shift
    prn1.io.sv <> sv
    prn2.io.sv <> sv

    val max_mag = Reg(UInt(23 bits)) init 0
    val max_idx = Reg(UInt(fft_size_log bits))
    val max_freq = Reg(SInt(shift.getWidth bits))
    val max_freq_fine = Reg(SInt(fft_size_log bits))

    val ref_phase = Reg(UInt(log2Up(period) bits))

    val mode_fine = Reg(Bool())

    // Initialize FFT config and flush sample FIFO
    val init: State = new State with EntryPoint {
      onStart {
        // Set FFT config to forward FFT
        fft.config_payload := 1
        fft.config_valid := True

        if (flush) {
          io.iq.ready := True
        }

        prn1.io.set := True
        prn2.io.set := True
      }

      whenIsActive {
        // Finish FFT config
        when(fft.inst.io.s_axis_config.fire) {
          fft.config_valid := False
        }

        // Flush FIFO to get fresh samples
        if (flush) {
          io.iq.ready := True

          when(io.iq.fire) {
            sample_counter.increment()
          }

          when(sample_counter === 16) {
            goto(samples_in)
            io.iq.ready := False
            sample_counter.clear()
          }
        } else {
          goto(samples_in)
        }
      }
    }

    // Get samples and perform FFT
    val samples_in: State = new State {
      // Normalize and offset by 1/2 bit to compensate for twos comp bias
      val real = iq_complex.c.re @@ U"6'b100000"
      val imag = iq_complex.c.im @@ U"6'b100000"
      val ref_done = Reg(Bool()) init False

      whenIsActive {
        io.iq.ready := fft.inst.io.s_axis_data.ready
        fft.data_in_valid := io.iq.valid
        fft.data_in_payload := imag ## real

        // Record phase of first sample
        when(io.iq.fire & ~ref_done) {
          ref_phase := to4096(iq_complex.t)
          ref_done := True
        }

        when(fft.inst.io.s_axis_data.fire) {
          sample_counter.increment()

          // Indicate last sample
          when(sample_counter === fft_size - 2) {
            fft.data_in_valid := True // TODO: I forget why this needs to force valid but it seems unnecessary and bad?
            fft.data_in_last := True
          }

          when(sample_counter === fft_size - 1) {
            goto(samples_out)
            sample_counter.clear()
            io.iq.ready := False
            fft.data_in_valid := False
            fft.data_in_last := False
          }
        }
      }
    }

    // Conjugate output of FFT and store in memory
    val samples_out: State = new State {
      whenIsActive {
        fft.data_out_ready := True

        when(fft.inst.io.m_axis_data.fire) {
          val data_out = fft.inst.io.m_axis_data.payload.data.as(Complex(fft_width))
          val data_conj = -data_out.im ## data_out.re

          sample_mem(sample_counter(0, fft_size_log bits)) := data_conj
          sample_counter.increment()

          when(sample_counter === fft_size - 1) {
            goto(prn_in)
            fft.data_out_ready := False
            sample_counter.clear()
          }
        }
      }
    }

    // Generate PRN and perform FFT
    val prn_in: State = new State {
      // Offset PRN to fix timing (TODO: I forget why)
      onEntry {
        prn1_ready := True
      }

      whenIsActive {
        // Scale PRN to +-1 (127/-128) and zero imaginary component
        val prn_extended = prn1.io.code.payload.asSInt.resize(8 bits) ^ S"8'b10000000"
        fft.data_in_payload := U"8'h0" ## prn_extended
        fft.data_in_valid := prn1.io.code.valid
        prn1_ready := True

        when(fft.inst.io.s_axis_data.fire) {
          sample_counter.increment()

          when(sample_counter === fft_size - 2) {
            fft.data_in_last := True
          }

          when(sample_counter === fft_size - 1) {
            goto(prn_out)
            sample_counter.clear()
            prn1_ready := False
            fft.data_in_valid := False
            fft.data_in_last := False
          }
        }
      }
    }

    // Store output of FFT in memory
    val prn_out: State = new State {
      whenIsActive {
        fft.data_out_ready := True

        when(fft.inst.io.m_axis_data.fire) {
          prn_mem(sample_counter(0, fft_size_log bits)) := fft.inst.io.m_axis_data.payload.data
          sample_counter.increment()

          when(sample_counter === fft_size - 1) {
            goto(mix)
            fft.data_out_ready := False
            sample_counter.clear()
          }
        }
      }
    }

    // Mix PRN and samples and do inverse FFT
    val mix: State = new State {
      val delay_counter = Reg(UInt(3 bits)) init 0
      val delay_threshold = 4 // Number of pipeline stages

      val prime = delay_counter < delay_threshold
      val advance = fft.inst.io.s_axis_data.ready | prime

      val s1_sample = Reg(Complex(fft_width))
      val s1_prn = Reg(Complex(fft_width))

      val s2_re_mix1 = Reg(SInt(16 bits))
      val s2_re_mix2 = Reg(SInt(16 bits))
      val s2_im_mix1 = Reg(SInt(16 bits))
      val s2_im_mix2 = Reg(SInt(16 bits))

      val s3_re_mix = Reg(SInt(16 bits))
      val s3_im_mix = Reg(SInt(16 bits))

      onEntry {
        fft.config_payload := 0
        fft.config_valid := True
      }

      whenIsActive {
        when(delay_counter < delay_threshold) {
          delay_counter := delay_counter + 1
        } otherwise {
          fft.data_in_valid := True
        }

        when(advance) {
          sample_counter.increment()

          // Stage 1 - get IQ sample and PRN sample
          s1_sample := sample_mem.readSync(sample_counter(0, fft_size_log bits)).as(Complex(fft_width))
          val prn_addr = sample_counter.value.intoSInt + shift // Do frequency shift
          s1_prn := prn_mem.readSync(prn_addr.asUInt(0, fft_size_log bits)).as(Complex(fft_width))

          // Stage 2 - TODO: implement this in different stages so only one DSP is used
          s2_re_mix1 := s1_sample.re * s1_prn.re
          s2_re_mix2 := s1_sample.im * s1_prn.im
          s2_im_mix1 := s1_sample.re * s1_prn.im
          s2_im_mix2 := s1_sample.im * s1_prn.re

          // Stage 3 - sum real and imaginary terms
          s3_re_mix := s2_re_mix1 - s2_re_mix2
          s3_im_mix := s2_im_mix1 + s2_im_mix2

          // Stage 4 - truncate back to 8 bits
          // 8 bits doesn't provide enough dynamic range, so we have to do the
          // mixing in 16 bits then truncate to 8 bits. The offset of 3 is a
          // guess of where the magnitude of the result might be. This
          // definitely cuts off bits in some cases, but still works.
          // TODO: do this better, maybe saturate with upper bits?
          val data_re = s3_re_mix.sign ## s3_re_mix(3, 7 bits)
          val data_im = s3_im_mix.sign ## s3_im_mix(3, 7 bits)
          fft.data_in_payload := data_im ## data_re

          when(sample_counter === fft_size + delay_threshold - 1) {
            fft.data_in_last := True
          } elsewhen (sample_counter === fft_size + delay_threshold) {
            sample_counter.clear()
            delay_counter := 0
            fft.data_in_valid := False
            fft.data_in_last := False

            mode_fine := False
            goto(evaluate)
          }
        }

        when(fft.inst.io.s_axis_config.fire) {
          fft.config_valid := False
        }
      }
    }

    // Process time domain results of IFFT and repeat
    val evaluate: State = new State {
      val sample = fft.inst.io.m_axis_data.payload.data.as(Complex(fft_width))

      // Set up magnitude approximator
      val mag = Magnitude()
      mag.io.re := 0
      mag.io.im := 0
      mag.io.ready := False

      val mag_delay = 5
      val mag_counter = Delay(sample_counter.value(0, fft_size_log bits), mag_delay)
      val mag_exp = Delay(fft.inst.io.m_axis_data.payload.user, mag_delay).asUInt
      // Hopefully exponent will never be greater than 4 bits (TODO: saturate)
      val mag_abs = mag.io.mag << mag_exp(0, 4 bits)
      val mag_valid = Delay(fft.inst.io.m_axis_data.fire, mag_delay)

      io.temp_fft_index <> max_idx
      io.temp_fft_val <> max_mag

      whenIsActive {
        fft.data_out_ready := True

        // TODO: pipeline these?
        mag.io.re := sample.re
        mag.io.im := sample.im
        mag.io.ready := fft.inst.io.m_axis_data.fire

        when(fft.inst.io.m_axis_data.fire) {
          sample_counter.increment()

          when(sample_counter === fft_size - 1) {
            sample_counter.clear()
          }
        }

        when(mag_valid) {
          when(mag_abs > max_mag) {
            max_mag := mag_abs

            when(mode_fine) {
              max_freq_fine := mag_counter.resized.asSInt // FFT frequencies are in twos comp order
            } otherwise {
              max_freq := shift
              max_idx := (mag_counter - ref_phase).resized
            }
          }

          when(mag_counter === fft_size - 1) {
            sample_counter.clear()

            when(mode_fine) {
              goto(results)
            } otherwise {
              when(shift === freq_shift) {
                goto(fine1)
              } otherwise {
                shift := shift + 1
                goto(mix)
              }
            }
          }
        }
      }
    }

    // Adjust PRN generate for code offset and flush sample FIFO
    val fine1: State = new State {
      /* All phases are converted to be out of 4096 before comparison
       * 
       * prn_phase is the absolute phase of the PRN generator
       * iq_phase is the relative phase of incoming samples
       * ref_phase is the relative phase of the first sample used for coarse acquisition
       * max_idx is measured phase offset, the number of samples that ref_phase is ahead of the absolute phase
       * 
       * max_idx - ref_phase is the absolute phase offset: add this to iq_phase to get the current absolute phase
       */

      val flush_done = Reg(Bool())

      val prn_phase = to4096(prn2.io.sample_count)
      val iq_phase_4096 = to4096(iq_complex.t)

      // Absolute offset of current IQ sample
      val iq_prn_offset = iq_phase_4096 + max_idx - ref_phase

      onEntry {
        flush_done := False

        // Set FFT config to forward FFT
        fft.config_payload := 1
        fft.config_valid := True
      }

      whenIsActive {
        // Flush FIFO
        io.iq.ready := True

        when(io.iq.fire) {
          sample_counter.increment()

          when(sample_counter === 16) {
            flush_done := True
          }
        }

        // Adjust PRN code
        // when(iq_prn_offset > prn_phase) {
          // prn2.io.code.ready := True
        // }

        // Only continue when codes align and FIFO is flushed
        // Use counts out of 4092 to prevent skipped counts
        val prn_sample_count_offset = UInt(12 bits)

        when (prn2.io.sample_count === 0) {
          prn_sample_count_offset := 4091
        } otherwise {
          prn_sample_count_offset := prn2.io.sample_count - 1
        }

        when((iq_complex.t === prn_sample_count_offset) & flush_done) {
          sample_counter.clear()
          goto(fine2)
        }

        // Finish FFT config
        when(fft.inst.io.s_axis_config.fire) {
          fft.config_valid := False
        }
      }
    }

    // Remove PRN, decimate, send to FFT
    val fine2: State = new State {
      val dec = Decimate(iq_size = 8, factor = 8)

      // Input buffers
      val buf_prn = Reg(Bool())
      val buf_iq = Reg(Complex(iq_size))
      val buf_prn_valid = Reg(Bool())
      val buf_iq_valid = Reg(Bool())
      
      // Mixed sample
      val dec_sample = Complex(8)
      dec_sample.re := (buf_prn ? buf_iq.re | -buf_iq.re) @@ U"6'b100000"
      dec_sample.im := (buf_prn ? buf_iq.im | -buf_iq.im) @@ U"6'b100000"
      // DEBUG:
      // dec_sample.re := (buf_prn ? buf_iq.re | buf_iq.re) @@ U"6'b100000"
      // dec_sample.im := (buf_prn ? buf_iq.im | buf_iq.im) @@ U"6'b100000"

      // Defaults
      dec.io.iq_in.payload := dec_sample.asBits
      dec.io.iq_out.ready := False

      val iq_in_valid = Reg(Bool()) init False
      dec.io.iq_in.valid := iq_in_valid

      onEntry {
        sample_counter.clear()

        buf_prn_valid := False
        buf_iq_valid := False
        iq_in_valid := False

        fft.data_in_valid := False // TODO: needed?

        dec_sample.re := 0
        dec_sample.im := 0
      }

      // Currently 2 cycles per sample, TODO: make single cycle
      whenIsActive {
        // If buffer is empty, wait for new sample
        io.iq.ready := !buf_iq_valid
        prn2.io.code.ready := !buf_prn_valid

        // Populate IQ buffer
        when (io.iq.fire) {
          buf_iq.re := iq_complex.c.re
          buf_iq.im := iq_complex.c.im
          buf_iq_valid := True
        }

        // Populate PRN buffer
        when (prn2.io.code.fire) {
          buf_prn := prn2.io.code.payload
          buf_prn_valid := True
        }

        // Consume both buffers
        when (buf_prn_valid && buf_iq_valid) {
          iq_in_valid := True

          buf_prn_valid := False
          buf_iq_valid := False
        } elsewhen (dec.io.iq_in.fire) {
          iq_in_valid := False
        }

        // Pipe decimated samples to FFT
        fft.data_in_payload := dec.io.iq_out.payload
        fft.data_in_valid := dec.io.iq_out.valid
        fft.data_in_last := sample_counter >= fft_size - 1
        dec.io.iq_out.ready := fft.inst.io.s_axis_data.ready

        when (dec.io.iq_out.fire) {
          sample_counter.increment()
        }

        when (fft.inst.io.s_axis_data.fire && fft.data_in_last) {
          fft.data_in_valid := False

          mode_fine := True
          max_mag := 0
          goto(evaluate)
        }
      }
    }

    // Send out results, increment SV, start over
    val results: State = new State {
      onEntry {
        sv := sv + 1
      }
    }
  }

  // Things for debugging that will be optimized out in synthesis
  val debug_area = new Area {
    val abs_sample_count = Counter(64 bits, io.iq.fire)
    val abs_prn2_count = prn2.debug_count.pull()
  }
}

object AcquisitionVerilog extends App {
  // Generate verilog for testbench. If freq_shift is changed, also change in tb.
  Config.spinal.generateVerilog(Acquisition(freq_shift = 1, flush = false))
}
