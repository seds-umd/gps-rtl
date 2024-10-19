package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.bus.amba4.axilite.AxiLite4SlaveFactory
import ethernet._
import ethernet.stream.{UdpStream, StreamAxiLite}

case class EthDecimate(out_size: Int = 64) extends Component {
  val io = new Bundle {
    val rx = slave Stream (Fragment(Bits(8 bits)))
    val tx = master Stream (Fragment(Bits(8 bits)))
  }

  val dut = Decimate(iq_in_size = 8, iq_out_size = 8, factor = 8)

  val rx_16b = Stream(Fragment(Bits(16 bits)))
  val rx_adapter = StreamWidthAdapter(io.rx, dut.io.iq_in)

  val tx_16b = dut.io.iq_out.addFragmentLast(Counter(out_size))
  val tx_adapter = StreamFragmentWidthAdapter(tx_16b, io.tx)
}

/* Address map:
 * 0x00 - write anything to hold reset for 10ms
 * 0x04 - 32 bit input sample counter, after width adapter (so it counts real samples)
 * 0x08 - 32 bit result counters
 * 0x0C - 8 bit LED control - 1 is off
 * 0x10 - FIFO availability
 * 0x100 - write anything to reset all cycle counters (which will then run for 100M cycles)
 * 0x104 - total cycles
 * 0x200 - early
 * 0x204 - prompt
 * 0x208 - late
 * 0x20C - carrier freq delta SFix(8 exp, 16 bits)
 * 0x210 - tracking config
 *  [5:0] - sv
 *  [17:6] - freq_offset
 *  [29:18] - phase_offset
 */

case class EthernetTestbench() extends Component {
  val io = new Bundle {
    val gtx_clk = in Bool ()
    val gtx_rst = in Bool ()

    val gmii = slave(GMII())
    val leds = out Bits (8 bits)
  }

  val udp = UdpStream(false)

  val reset_timeout = Timeout(10 ms)

  val stream_axil = StreamAxiLite()
  udp.addPort(1000, stream_axil.io.tx, stream_axil.io.rx)
  val bus_ctrl = AxiLite4SlaveFactory(stream_axil.io.axil)
  bus_ctrl.onWrite(0x00)(reset_timeout.clear())

  bus_ctrl.drive(io.leds, 0x0c, 0)

  val rst_area = new ResetArea(!reset_timeout, true) {
    udp.io.gtx_clk := io.gtx_clk
    udp.io.gtx_rst := io.gtx_rst
    udp.io.gmii <> io.gmii

    udp.io.mac := B"h00_00_01_00_00_02"
    udp.io.ip := B"8'd10" ## B"8'd0" ## B"8'd0" ## B"8'd2"
    udp.io.gateway := B"8'd10" ## B"8'd0" ## B"8'd0" ## B"8'd1"
    udp.io.subnet := 0

    val iq_stream = Stream(Fragment(Bits(8 bits)))

    val acq = AcquisitionModular(freq_shift = 2, flush = false, debug = true)
    val (iq_stream_unfragmented, iq_availability) = iq_stream.toStreamOfFragment.queueWithAvailability(100000)
    val iq_full_bits = StreamWidthAdapter.make(iq_stream_unfragmented, acq.io.iq.payloadType)
    val iq_forked = StreamFork(iq_full_bits, 2)
    acq.io.iq << iq_forked(0)

    udp.addPort(1010, acq.io.results.fragmentTransaction(8), iq_stream)

    val input_counter = Counter(32 bits, acq.io.iq.fire)
    bus_ctrl.read(input_counter.value, 0x04)

    val result_counter = Counter(32 bits, acq.io.results.fire)
    bus_ctrl.read(result_counter.value, 0x08)

    // Acquisition cycle counting
    val cycles_reset_timeout = Timeout(1 ms)
    val cycles_total = Counter(32 bits)
    val cycles_stalled = Counter(32 bits)
    val cycles_empty = Counter(32 bits)

    when(cycles_total < 100 * 1000 * 1000 && cycles_reset_timeout) {
      cycles_total.increment()

      when(acq.io.iq.ready && !acq.io.iq.valid) {
        cycles_empty.increment()
      }
      when(!acq.io.iq.ready & acq.io.iq.valid) {
        cycles_stalled.increment()
      }
    }

    bus_ctrl.onRead(0x100) {
      cycles_total.clear()
      cycles_stalled.clear()
      cycles_empty.clear()
      cycles_reset_timeout.clear()
    }

    printf("Availability width: %d\n", iq_availability.getWidth)
    bus_ctrl.read(iq_availability, 0x10)

    // CORDIC testing
    val cordic = XilinxCORDIC()
    val cordic_phase_8b = Stream(Fragment(Bits(8 bits)))
    val cordic_adapter = StreamWidthAdapter(cordic_phase_8b, cordic.io.phase, padding = true)
    udp.addPort(1020, cordic.io.dout.fragmentTransaction(8), cordic_phase_8b)

    // Tracking channel
    val tracking = TrackingChannel()
    tracking.io.iq << iq_forked(1).map(_.as(ComplexTimestamp()))
    bus_ctrl.readStreamNonBlocking(tracking.io.early, 0x200, 31, 0)
    bus_ctrl.readStreamNonBlocking(tracking.io.prompt, 0x204, 31, 0)
    bus_ctrl.readStreamNonBlocking(tracking.io.late, 0x208, 31, 0)
    bus_ctrl.driveFlow(tracking.io.freq_delta, 0x20c)

    // Config
    val tracking_config = Flow(AcquisitionResults())
    tracking_config.valid.setAsReg()
    tracking.io.config << tracking_config
    bus_ctrl.drive(tracking_config.sv, 0x210, 0)
    bus_ctrl.drive(tracking_config.freq_offset, 0x210, 6)
    bus_ctrl.drive(tracking_config.phase_offset, 0x210, 18)
    tracking_config.snr := 0
    bus_ctrl.onWrite(0x210)(tracking_config.valid := True)
    when(tracking_config.valid)(tracking_config.valid := False)
  }
}

object EthernetTestbenchVerilog extends App {
  val report = EthConfig.spinal.generateVerilog(EthernetTestbench())
  report.mergeRTLSource("sources")
}
