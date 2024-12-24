package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.bus.amba4.axilite.AxiLite4SlaveFactory
import ethernet._
import ethernet.stream.{UdpStream, StreamAxiLite}

/* Address map:
 * 0x00 - write anything to hold reset for 10ms
 * 0x04 - 32 bit input sample counter, after width adapter (so it counts real samples)
 * 0x08 - 32 bit result counters
 * 0x0C - 8 bit LED control - 1 is off
 * 0x10 - FIFO availability
 * 0x100 - write anything to reset all cycle counters (which will then run for 100M cycles)
 * 0x104 - total cycles
 * 0x210-0x217 - tracking config
 * 0x300 - write MAX2769 SPI config data
 *
 * Debug counters - write to any one of them to start count, they store count
 * of rising edges in 1 ms period (based on 200 MHz clk)
 * 0x310 - MAX2769 CLK_SER counter
 * 0x314 - MAX2769 DATA_OUT counter
 * 0x318 - MAX2769 DATA_SYNC counter
 *
 * 0xFFC - unix timestamp of spinalhdl build
 *
 * Ports:
 * 1000 - AXI-L reads and writes
 * 1010 - Acquisition data and results
 * 1020 - CORDIC sin/cos
 * 1021 - CORDIC atan
 * 1030 - MAX2769 IQ data
 * 1040 - tracking
 */

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

case class EthernetTestbench(config: GpsConfig) extends Component {
  val io = new Bundle {
    val gtx_clk = in Bool ()
    val gtx_rst = in Bool ()

    val gmii = slave(GMII())
    val leds = out Bits (8 bits)

    val spi = master(SpiBundle())
    val max = MaxDspBus()
  }

  val reset_timeout = Timeout(10 ms)

  // UDP stack outside soft reset, it doesn't reset properly inside
  val udp = UdpStream()
  udp.io.gtx_clk := io.gtx_clk
  udp.io.gtx_rst := io.gtx_rst
  udp.io.gmii <> io.gmii

  udp.io.mac := B"h02_00_01_00_00_02"
  udp.io.ip := B"8'd10" ## B"8'd0" ## B"8'd0" ## B"8'd2"
  udp.io.gateway := B"8'd10" ## B"8'd0" ## B"8'd0" ## B"8'd1"
  udp.io.subnet := 0

  val stream_axil = StreamAxiLite()
  udp.addPort(1000, stream_axil.io.tx, stream_axil.io.rx)
  val bus_ctrl = AxiLite4SlaveFactory(stream_axil.io.axil)
  bus_ctrl.onWrite(0x00)(reset_timeout.clear())

  bus_ctrl.drive(io.leds, 0x0c) init 0xff

  val timestamp = System.currentTimeMillis / 1000
  printf("Current timestamp: %d\n", timestamp)
  bus_ctrl.read(U(timestamp, 32 bits), 0xffc)

  val rst_area = new ResetArea(!reset_timeout, true) {

    val acquisition_area = config.eth_acquisition generate new Area {
      val iq_stream = Stream(Fragment(Bits(8 bits)))

      val acq = AcquisitionModular(freq_shift = 20, flush = false, debug = true)
      val (iq_stream_unfragmented, iq_availability) =
        iq_stream.toStreamOfFragment.queueWithAvailability(20000, forFMax = true)
      val iq_full_bits = ComplexTimestamper(StreamWidthAdapter.make(iq_stream_unfragmented, Complex(2)))
      acq.io.iq << iq_full_bits.map(_.asBits)

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

      bus_ctrl.read(iq_availability, 0x10)
    }

    val cordic_area = config.eth_cordic generate new Area {
      // Sin/Cos CORDIC
      val cordic = CordicSinCos()
      val cordic_phase_8b = Stream(Fragment(Bits(8 bits)))
      val cordic_adapter = StreamWidthAdapter(cordic_phase_8b.toStreamOfFragment, cordic.io.phase, padding = true)
      udp.addPort(1020, cordic.io.dout.fragmentTransaction(8), cordic_phase_8b)

      // Atan CORDIC
      val cordic_atan = CordicAtan()
      val cordic_xy_8b = Stream(Fragment(Bits(8 bits)))
      val cordic_xy_adapter = StreamWidthAdapter(cordic_xy_8b.toStreamOfFragment, cordic_atan.io.xy, padding = true)
      udp.addPort(1021, cordic_atan.io.dout.fragmentTransaction(8), cordic_xy_8b)
    }

    // Tracking
    val tracking_area = config.eth_tracking generate new Area {
      val tracking = TrackingChannel(config)
      tracking.io.nav_data.freeRun()

      val iq_fragment = Stream(Fragment(Bits(8 bits)))
      val (iq_stream, _) =
        iq_fragment.toStreamOfFragment.queueWithAvailability(200)
      val iq_2b =
        ComplexTimestamper(StreamWidthAdapter.make(iq_stream, Complex(2)), period = config.prn_period)
      tracking.io.iq << iq_2b
      val results_8b = tracking.io.debug.toStream.queue(10).fragmentTransaction(8)
      udp.addPort(1040, results_8b, iq_fragment)

      bus_ctrl.driveFlow(tracking.io.config_flow, 0x210)

      val sample_count = Counter(32 bits, tracking.io.iq.fire)
      val result_count = Counter(32 bits, tracking.io.debug.fire)
      bus_ctrl.read(sample_count.value, 0x200)
      bus_ctrl.read(result_count.value, 0x204)

      // Hash for debugging
      val input_hash = Reg(UInt(32 bits)) init 0
      val in_idx = Reg(UInt(1 bits)) init 0
      val output_hash = Reg(Bits(32 bits)) init 0
      val out_idx = Reg(UInt(2 bits)) init 0

      when (results_8b.fire) {
        // input_hash(16*in_idx, 16 bits) := input_hash(16*in_idx, 16 bits) ^ iq_2b.payload.asBits
        // input_hash(0, 16 bits) := input_hash(0, 16 bits) + iq_2b.c.asBits.asUInt
        // input_hash(16, 16 bits) := input_hash(16, 16 bits) + iq_2b.t
        input_hash := input_hash + iq_2b.t
        output_hash := iq_2b.t.asBits.resized
        in_idx := in_idx + 1
        // output_hash(8*out_idx, 8 bits) := output_hash(8*out_idx, 8 bits) ^ results_8b.payload
        out_idx := out_idx + 1
      }
      bus_ctrl.read(input_hash, 0x20C)
      bus_ctrl.read(output_hash, 0x208)
    }

    // MAX2769
    val max_area = config.eth_max2769 generate new Area {
      val config = MaxSpiConfig(div = 20, prog_defaults = false)
      config.io.spi <> io.spi

      val dsp = MaxInterface()
      io.max <> dsp.io.max
      val dsp_iq = Stream(Bits(8 bits))
      val iq_adapter = StreamWidthAdapter(dsp.io.iq.map(_.c), dsp_iq)

      val config_flow = Flow(Bits(32 bits))
      bus_ctrl.driveFlow(config_flow, 0x300)
      config.io.data << config_flow.toStream

      val dummy_stream = Stream(Fragment(Bits(8 bits)))
      dummy_stream.ready := True
      val stopped = Reg(Bool()) init True
      when(dummy_stream.fire) {
        // Send 0 to start, 1 to stop
        stopped := dummy_stream.payload(0)
      }
      udp.addPort(1030, dsp_iq.throwWhen(stopped).addFragmentLast(Counter(500)), dummy_stream)
    }

    // Frequency counter for interface status
    val max_counters = config.eth_max2769 generate new Area {
      val period = 10 ms
      val counter_width = log2Up((period * (16.368 MHz)).toInt)

      val max_clk_area = new ClockingArea(max_area.dsp.max_domain) {
        val clk = Counter(counter_width bits, True)
        val data = Counter(counter_width bits, io.max.data_in.asBool)
        val sync = Counter(counter_width bits, io.max.data_sync.rise)
      }

      val timer = Timeout(period)

      val clk_val = Reg(UInt(counter_width bits))
      val data_val = Reg(UInt(counter_width bits))
      val sync_val = Reg(UInt(counter_width bits))

      def start_counters() = {
        clk_val := BufferCC(max_clk_area.clk.value)
        data_val := BufferCC(max_clk_area.data.value)
        sync_val := BufferCC(max_clk_area.sync.value)
        timer.clear()
      }

      when(timer.stateRise) {
        clk_val := BufferCC(max_clk_area.clk.value) - clk_val
        data_val := BufferCC(max_clk_area.data.value) - data_val
        sync_val := BufferCC(max_clk_area.sync.value) - sync_val
      }

      bus_ctrl.onWrite(0x310)(start_counters())
      bus_ctrl.onWrite(0x314)(start_counters())
      bus_ctrl.onWrite(0x318)(start_counters())
      bus_ctrl.read(clk_val, 0x310)
      bus_ctrl.read(data_val, 0x314)
      bus_ctrl.read(sync_val, 0x318)
    }

    // Handle signals
    val max_defaults = !config.eth_max2769 generate new Area {
      io.spi.cs := True
      io.spi.sclk := False
      io.spi.sdata := False
    }
  }
}

object EthernetTestbenchVerilog extends App {
  val config = GpsConfig(debug = true)

  val report = EthConfig.spinal.generateVerilog(EthernetTestbench(config))
  report.mergeRTLSource("sources")
}
