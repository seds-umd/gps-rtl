package gps

import spinal.core._
import spinal.lib._

case class MaxInterface(iq_size: Int = 2, period: Int = 4092) extends Component {
  val io = new Bundle {
    // MAX2769 interface
    val clk_ser = in Bool ()
    val data_in = in UInt (1 bit)
    val data_sync = in Bool ()
    val time_sync = in Bool ()

    // FPGA interface
    // val clk = in Bool ()
    // val rst = in Bool ()
    val iq = master Stream (ComplexTimestamp(iq_size, period).asBits)
  }

  val fpga_domain = ClockDomain.current
  val max_domain = ClockDomain(io.clk_ser, fpga_domain.reset)

  val sample_fifo = StreamFifoCC(
    dataType = ComplexTimestamp(iq_size, period).asBits,
    depth = 8,
    pushClock = max_domain,
    popClock = fpga_domain
  )

  sample_fifo.io.pop >> io.iq

  val max_area = new ClockingArea(max_domain) {
    val phase_counter = Counter(period)

    val fifo_push_payload = ComplexTimestamp(iq_size, period)
    sample_fifo.io.push.payload := fifo_push_payload.asBits

    val bit_counter = Reg(UInt(4 bits)) init 0 // up to 16
    val bit_index = Reg(UInt(2 bits)) init 0 // up to 4

    // Store incoming samples
    val sample_reg = Vec.fill(2)(Vec.fill(2 * iq_size)(Reg(UInt(16 bits)) init 0))
    val reg_index = Reg(UInt(1 bit)) init 0
    val dump_reg = Reg(Bool()) init False

    val input_valid = ((bit_counter === 0) & (io.data_sync)) | ((bit_counter =/= 0))

    // Wait for data sync before starting frame
    when(input_valid) {
      bit_counter := bit_counter + 1

      // Advance index
      when(bit_counter === 15) {
        bit_index := bit_index + 1

        when(bit_index === 2 * iq_size - 1) {
          dump_reg := True
          reg_index := ~reg_index
        }
      }

      // Shift in new data bit
      sample_reg(reg_index)(bit_index) := io.data_in @@ sample_reg(reg_index)(bit_index)(1, 15 bits)
    }

    sample_fifo.io.push.valid := False
    fifo_push_payload.c.re := 0
    fifo_push_payload.c.im := 0
    fifo_push_payload.t := phase_counter

    val dump_bit_index = Reg(UInt(4 bits)) init 0 // up to 16

    // Dump registers to FIFO
    when(dump_reg) {
      dump_bit_index := dump_bit_index + 1

      phase_counter.increment()

      sample_fifo.io.push.valid := True

      if (iq_size == 1) {
        fifo_push_payload.c.re := sample_reg(~reg_index)(0)(dump_bit_index).asSInt
        fifo_push_payload.c.im := sample_reg(~reg_index)(1)(dump_bit_index).asSInt
      } else {
        fifo_push_payload.c.re := (sample_reg(~reg_index)(0)(dump_bit_index) ## 
                                sample_reg(~reg_index)(1)(dump_bit_index)).asSInt
        fifo_push_payload.c.im := (sample_reg(~reg_index)(2)(dump_bit_index) ## 
                                sample_reg(~reg_index)(3)(dump_bit_index)).asSInt
      }

      // Stop when out of bits unless new bits are ready
      when((dump_bit_index === 15)) {
        dump_reg := False
      }
    }
  }
}

object MaxInterfaceVerilog extends App {
  Config.spinal.generateVerilog(MaxInterface(2))
}
