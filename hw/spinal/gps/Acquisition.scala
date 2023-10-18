package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

/* TODO
 * Handle FFT aresetn and aclken
 *
 */

case class Acquisition(iq_size: Int = 2, fft_size: Int = 4096) extends Component {
  val fft_size_log = log2Up(fft_size)

  val io = new Bundle {
    val iq = slave Stream (Complex(iq_size).asBits)

    val valid_sv = in Bits(32 bits)

    val temp_fft_index = out UInt(fft_size_log bits)
    val temp_fft_val = out UInt(9 bits)
  }

  io.iq.ready := False

  val sample_mem = Mem(Complex(8), wordCount = fft_size)
  val prn_mem = Mem(Complex(8), wordCount = fft_size)

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

    val status_ready = Reg(Bool()) init True
    inst.io.m_axis_status.ready <> status_ready
  }

  val prn = PRN()
  val prn_ready = Reg(Bool()) init False
  prn.io.inc := U"17'h4000" // TODO: automatically calculate based on sample rate
  prn.io.set := False
  prn.io.code.ready := prn_ready

  val fsm = new StateMachine {
    val sample_counter = Reg(UInt(fft_size_log bits)) init 0
    val sv_current = Reg(UInt(6 bits)) init 0
    prn.io.sv <> sv_current

    // Initialize FFT config and flush sample FIFO
    val init = new State with EntryPoint {
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
          sample_counter := sample_counter + 1
        }

        when(sample_counter === 32) {
          goto(samples_in)
          io.iq.ready := False
          sample_counter := 0
        }
      }
    }

    // Get samples and perform FFT
    val samples_in = new State {
      val iq_c = io.iq.payload.as(Complex(iq_size))

      whenIsActive {
        io.iq.ready := fft.inst.io.s_axis_data.ready
        fft.data_in_valid := io.iq.valid
        fft.data_in_payload := (iq_c.im.resize(8 bits) ## iq_c.re.resize(8 bits))

        when(fft.inst.io.s_axis_data.fire) {
          sample_counter := sample_counter + 1

          when(sample_counter === fft_size - 2) {
            fft.data_in_last := True
          }

          when(sample_counter === fft_size - 1) {
            goto(samples_out)
            sample_counter := 0
            io.iq.ready := False
            fft.data_in_valid := False
            fft.data_in_last := False
          }
        }
      }
    }

    // Process output of FFT and store in memory
    val samples_out = new State {
      whenIsActive {
        fft.data_out_ready := True

        when(fft.inst.io.m_axis_data.fire) {
          sample_mem(sample_counter) := fft.inst.io.m_axis_data.payload.data.as(Complex(8))
          sample_counter := sample_counter + 1

          when(sample_counter === fft_size - 1) {
            goto(prn_in)
            fft.data_out_ready := False
          }
        }
      }
    }

    // Generate PRN and perform FFT
    val prn_in = new State {
      whenIsActive{
        // TODO: sign extend PRN?
        fft.data_in_payload := U"8'h0" ## prn.io.code.payload.asUInt.resize(8 bits)
        fft.data_in_valid := prn.io.code.valid
        prn_ready := fft.inst.io.s_axis_data.ready

        when(fft.inst.io.s_axis_data.fire) {
          sample_counter := sample_counter + 1

          when(sample_counter === fft_size - 2) {
            fft.data_in_last := True
          }

          when(sample_counter === fft_size - 1) {
            goto(prn_out)
            sample_counter := 0
            fft.data_in_valid := False
            prn_ready := False
            fft.data_in_last := False
          }
        }
      }
    }

    // Store output of FFT in memory
    val prn_out = new State {
      whenIsActive {
        fft.data_out_ready := True

        when(fft.inst.io.m_axis_data.fire) {
          prn_mem(sample_counter) := fft.inst.io.m_axis_data.payload.data.as(Complex(8))
          sample_counter := sample_counter + 1

          when(sample_counter === fft_size - 1) {
            goto(mix)
            fft.data_out_ready := False
          }
        }
      }
    }

    // Mix PRN and samples and do inverse FFT
    val mix = new State {
      whenIsActive {
        val curr_sample = sample_mem(sample_counter)
        val curr_prn = prn_mem(sample_counter)

        // TODO: time multiplex multiplications
        val re_mix = curr_sample.re * curr_prn.re - curr_sample.im * curr_prn.re
        val im_mix = curr_sample.re * curr_prn.im - curr_sample.im * curr_prn.re
        
        // Use 8 most significant bits of each
        fft.data_in_payload := im_mix(8, 8 bits) ## re_mix(8, 8 bits)
        fft.data_in_valid := True

        when(fft.inst.io.s_axis_data.fire) {
          sample_counter := sample_counter + 1

          when(sample_counter === fft_size - 2) {
            fft.data_in_last := True
          }

          when(sample_counter === fft_size - 1) {
            // goto(evaluate)
            sample_counter := 0
            fft.data_in_valid := False
            fft.data_in_last := False
            // sv_current := sv_current + 1
          }
        }
      }
    }

    // Process time domain results of IFFT and repeat
    val evaluate = new State {
      val max = Reg(UInt(9 bits)) init 0
      val max_idx = Reg(UInt(fft_size_log bits)) init 0
      val curr_sample = fft.inst.io.m_axis_data.payload.data.as(Complex(8))
      val curr_mag = curr_sample.re.asUInt +^ curr_sample.im.asUInt // TODO: proper magnitude
      io.temp_fft_index <> max_idx
      io.temp_fft_val <> max

      whenIsActive {
        fft.data_out_ready := True

        when(fft.inst.io.m_axis_data.fire) {
          sample_counter := sample_counter + 1

          when(curr_mag > max) {
            max := curr_mag
            max_idx := sample_counter
          }

          when(sample_counter === fft_size - 1) {
            goto(temp)
            fft.data_out_ready := False
          }
        }
      }
    }

    val temp = new State{}

    // Fine acquisition
  }
}

object AcquisitionVerilog extends App {
  Config.spinal.generateVerilog(Acquisition())
}
