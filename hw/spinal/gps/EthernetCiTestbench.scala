package gps

import spinal.core._
import spinal.lib._
import ethernet._
import ethernet.stream.{UdpStream, StreamAxiLite}
import spinal.lib.bus.amba4.axilite.AxiLite4SlaveFactory
import spinal.lib.bus.misc.BusSlaveFactory

/*  Memory map:
 *
 * 0x0000-0x00FF - config
 * 0x0000 - reset
 * Bit 0 - Acquisition reset
 * 0x0004 - timestamp
 * 0x0008 - scratch
 *
 * 0x0100-0x01FF - tbd
 * 
 * Port map:
 * 1000 - AXI-L bus
 */

case class EthernetCiTestbench(config: GpsConfig) extends Component {
  val ACQ_FIFO_SIZE = 10000
  val RESET_ADDR = 0x0000

  val io = new Bundle {
    val mii = slave(MII())

    val spi = master(SpiBundle())
    val max = MaxDspBus()
  }

  val udp = UdpStream(sim = config.sim, use_gmii = false)
  udp.io.gtx_clk := False
  udp.io.gtx_rst := False
  udp.io.mii <> io.mii

  // IP/MAC configuration
  udp.io.mac := B"h02_00_01_00_00_03"
  udp.io.ip := B"8'd192" ## B"8'd168" ## B"8'd200" ## B"8'd2"
  udp.io.gateway := B"8'd192" ## B"8'd168" ## B"8'd200" ## B"8'd1"
  udp.io.subnet := B"8'd255" ## B"8'd255" ## B"8'd255" ## B"8'd0"

  // UDP to AXI-Lite controller
  val stream_axil = StreamAxiLite()
  val bus_ctrl = AxiLite4SlaveFactory(stream_axil.io.axil)
  udp.addPort(1000, stream_axil.io.tx, stream_axil.io.rx)

  // Resets
  val reset_period = if (config.sim) 5 us else 10 ms
  val reset_timeout = Timeout(reset_period)
  bus_ctrl.onWrite(RESET_ADDR)(reset_timeout.clear())

  val config_area = new Area {
    // Timestamp - will break on 19 January 2038
    val timestamp = System.currentTimeMillis / 1000
    printf("Current timestamp: %d\n", timestamp)
    bus_ctrl.read(U(timestamp, 32 bits), 0x0004)

    // Scratch
    val scratch = bus_ctrl.createReadAndWrite(Bits(32 bits), 0x0008)
  }

  val reset_area = new ResetArea(!reset_timeout, true) {
    val acquisition_area = new Area {
      val acquisition = AcquisitionModular(config, flush = false, debug = true)
      val input_stream = Stream(Fragment(Bits(8 bits)))
      val output_stream = Stream(Fragment(Bits(8 bits)))

      val (input_fragment, input_avail) = input_stream.toStreamOfFragment.queueWithAvailability(ACQ_FIFO_SIZE)
      val input_full = ComplexTimestamper(StreamWidthAdapter.make(input_fragment, Complex(2)))
      acquisition.io.iq << input_full.map(_.asBits)
      // input_stream.freeRun()
      output_stream << acquisition.io.results.fragmentTransaction(8)

      udp.addPort(1010, output_stream, input_stream)
    }

    val max2769_area = new Area {
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

    // acquisition_area.acquisition.io.iq << max2769_area.dsp.io.iq.map(_.asBits)
  }
}

object EthernetTestbenchCiVerilog extends App {
  val config = GpsConfig()

  val report = EthConfig.spinal.generateVerilog(EthernetCiTestbench(config))
  report.mergeRTLSource("sources")
}
