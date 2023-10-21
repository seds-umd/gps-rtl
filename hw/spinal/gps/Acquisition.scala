package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

/* TODO
 * Handle FFT aresetn and aclken
 * Figure out timing for code phase (some kind of reference timer?)
 */

case class Acquisition(iq_size: Int = 2, fft_size: Int = 4096, freq_shift: Int = 24) extends Component {
  val fft_size_log = log2Up(fft_size)

  val io = new Bundle {
    val iq = slave Stream (Complex(iq_size).asBits)

    // val temp_fft_index = out UInt(fft_size_log bits)
    // val temp_fft_val = out UInt(9 bits)
  }

  io.iq.ready := False

  val sample_mem = Mem(Complex(8).asBits, wordCount = fft_size)
  val prn_mem = Mem(Complex(8).asBits, wordCount = fft_size)
  sample_mem.addAttribute("ram_style", "block")
  prn_mem.addAttribute("ram_style", "block")

  val fft = new Area {
    val inst = XilinxFFT()

    val config_valid = Reg(Bool()) init False
    val config_payload = Reg(Bits(8 bits)) init 0

    inst.io.s_axis_config.valid <> config_valid
    inst.io.s_axis_config.payload.data <> config_payload

    val data_in_valid = Reg(Bool()) init False
    val data_in_payload = Reg(Bits(16 bits)) init 0
    val data_in_last = Reg(Bool()) init False

    inst.io.s_axis_data.valid <> data_in_valid
    inst.io.s_axis_data.payload.data <> data_in_payload
    inst.io.s_axis_data.last <> data_in_last

    val data_out_ready = Reg(Bool()) init False
    inst.io.m_axis_data.ready <> data_out_ready

    // val status_ready = Reg(Bool()) init True
    // inst.io.m_axis_status.ready <> status_ready
    inst.io.m_axis_status.ready := True // Don't need status stream
  }

  val prn = PRN()
  val prn_ready = Reg(Bool()) init False
  prn.io.inc := U"17'h4000" // TODO: automatically calculate based on sample rate
  prn.io.set := False
  prn.io.code.ready := prn_ready

  val fsm = new StateMachine {
    val sample_counter = Counter(fft_size_log + 1 bits) // TODO: better to split this up for each state?
    val sv = Reg(UInt(6 bits)) init 0
    val shift = Reg(SInt(log2Up(freq_shift * 2 + 1) bits)) init -freq_shift
    prn.io.sv <> sv

    // Initialize FFT config and flush sample FIFO
    val init : State = new State with EntryPoint {
      onStart {
        fft.config_payload := 1
        fft.config_valid := True

        io.iq.ready := True
        prn.io.set := True
      }

      whenIsActive {
        io.iq.ready := True

        when(fft.inst.io.s_axis_config.fire) {
          fft.config_valid := False
        }

        when(io.iq.fire) {
          sample_counter.increment()
        }

        when(sample_counter === 32) {
          goto(samples_in)
          io.iq.ready := False
          sample_counter.clear()
        }
      }
    }

    // Get samples and perform FFT
    val samples_in : State = new State {
      val iq_c = io.iq.payload.as(Complex(iq_size))

      whenIsActive {
        io.iq.ready := fft.inst.io.s_axis_data.ready
        fft.data_in_valid := io.iq.valid
        fft.data_in_payload := (iq_c.im.resize(8 bits) ## iq_c.re.resize(8 bits))

        when(fft.inst.io.s_axis_data.fire) {
          sample_counter.increment()

          when(sample_counter === fft_size - 2) {
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

    // Process output of FFT and store in memory
    val samples_out : State = new State {
      whenIsActive {
        fft.data_out_ready := True

        when(fft.inst.io.m_axis_data.fire) {
          val data1 = fft.inst.io.m_axis_data.payload.data.as(Complex(8))
          val data2 = -data1.im ## data1.re
          sample_mem(sample_counter(0, fft_size_log bits)) := data2
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
    val prn_in : State = new State {
      whenIsActive {
        // Sign extend PRN and set imaginary component to zero
        fft.data_in_payload := U"8'h0" ## prn.io.code.payload.asSInt.resize(8 bits)
        fft.data_in_valid := prn.io.code.valid
        prn_ready := fft.inst.io.s_axis_data.ready

        when(fft.inst.io.s_axis_data.fire) {
          sample_counter.increment()

          when(sample_counter === fft_size - 2) {
            fft.data_in_last := True
          }

          when(sample_counter === fft_size - 1) {
            goto(prn_out)
            sample_counter.clear()
            prn_ready := False
            fft.data_in_valid := False
            fft.data_in_last := False
          }
        }
      }
    }

    // Store output of FFT in memory
    val prn_out : State = new State {
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
    val mix : State = new State {
      // TODO: shift PRN
      val delay_counter = Reg(UInt(3 bits)) init 0
      val delay_threshold = 4 // Number of pipeline stages

      val prime = delay_counter < delay_threshold
      val advance = fft.inst.io.s_axis_data.ready | prime

      val s1_sample = Reg(Complex(8))
      val s1_prn = Reg(Complex(8))

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

          // Stage 1
          s1_sample := sample_mem.readSync(sample_counter(0, fft_size_log bits)).as(Complex(8))
          val prn_addr = sample_counter.value.intoSInt + shift // Do frequency shift
          s1_prn := prn_mem.readSync(prn_addr.asUInt(0, fft_size_log bits)).as(Complex(8))

          // Stage 2 - TODO: implement this in different stages so only one DSP is used
          s2_re_mix1 := s1_sample.re * s1_prn.re
          s2_re_mix2 := s1_sample.im * s1_prn.im
          s2_im_mix1 := s1_sample.re * s1_prn.im
          s2_im_mix2 := s1_sample.im * s1_prn.re

          // Stage 3
          s3_re_mix := s2_re_mix1 - s2_re_mix2
          s3_im_mix := s2_im_mix1 + s2_im_mix2

          // Stage 4
          fft.data_in_payload := s3_im_mix(8, 8 bits) ## s3_re_mix(8, 8 bits)

          when(sample_counter === fft_size + delay_threshold - 1) {
            fft.data_in_last := True
          } elsewhen (sample_counter === fft_size + delay_threshold) {
            sample_counter.clear()
            delay_counter := 0
            fft.data_in_valid := False
            fft.data_in_last := False
            goto(evaluate)
          }
        }

        when(fft.inst.io.s_axis_config.fire) {
          fft.config_valid := False
        }
      }
    }

    // Process time domain results of IFFT and repeat
    val evaluate : State = new State {
      val sample = fft.inst.io.m_axis_data.payload.data.as(Complex(8))

      val mag = Magnitude()
      mag.io.re := 0
      mag.io.im := 0
      mag.io.ready := False

      val mag_delay = 5 // TODO: verify delay
      val mag_counter = Delay(sample_counter.value(0, fft_size_log bits), mag_delay)
      val mag_exp = Delay(fft.inst.io.m_axis_data.payload.user, mag_delay).asUInt
      val mag_abs = mag.io.mag << mag_exp(0, 4 bits) // Hopefully exponent will never be greater than 15
      val mag_valid = Delay(fft.inst.io.m_axis_data.fire, mag_delay)

      val max_mag = Reg(UInt(23 bits)) init 0
      val max_idx = Reg(UInt(fft_size_log bits))
      val max_freq = Reg(SInt(shift.getWidth bits))

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
            // fft.data_out_ready := False
          }
        }

        when(mag_valid) {
          when(mag_abs > max_mag) {
            max_mag := mag_abs
            max_idx := mag_counter
            max_freq := shift
          }

          when(mag_counter === fft_size - 1) {
            when(shift === freq_shift) {
              goto(results)
            } otherwise {
              shift := shift + 1
              goto(mix)
            }
          }
        }
      }
    }

    // Send out results, increment SV, start over
    val results : State = new State {}

    // Fine acquisition
  }
}

object AcquisitionVerilog extends App {
  Config.spinal.generateVerilog(Acquisition(freq_shift = 2))
}
