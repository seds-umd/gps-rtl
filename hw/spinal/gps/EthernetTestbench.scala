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
  val rx_adapter = StreamFragmentWidthAdapter(io.rx, rx_16b)
  dut.io.iq_in << rx_16b.translateInto(Stream(Complex(8)))((to, from) => {
    to.assignFromBits(from)
  })

  val tx_16b = dut.io.iq_out.addFragmentLast(Counter(out_size))
  val tx_adapter = StreamFragmentWidthAdapter(tx_16b, io.tx)
}

/* Address map:
 * 0x00 - write anything to hold reset for 10ms
 * 0x04 - 32 bit input sample counter, after width adapter (so it counts real samples)
 * 0x08 - 32 bit result counters
 * 0x0C - 8 bit LED control - 1 is off
 * 0x10 - FIFO availability
 */

case class EthernetTestbench() extends Component {
  val time_speedup = 4

  val io = new Bundle {
    val gtx_clk = in Bool ()
    val gtx_rst = in Bool ()

    val gmii = slave(GMII())
    val leds = out Bits(8 bits)
  }

  val udp = UdpStream(false)

  val reset_timeout = Timeout(time_speedup*10 ms)

  val stream_axil = StreamAxiLite()
  udp.addPort(1000, stream_axil.io.tx, stream_axil.io.rx)
  val bus_ctrl = AxiLite4SlaveFactory(stream_axil.io.axil)
  bus_ctrl.onWrite(0x00)(reset_timeout.clear())

  bus_ctrl.drive(io.leds, 0x0C, 0)

  val rst_area = new ResetArea(!reset_timeout, true) {
    // --- Ethernet / GMII wiring ---
    udp.io.gtx_clk := io.gtx_clk
    udp.io.gtx_rst := io.gtx_rst
    udp.io.gmii    <> io.gmii

    // --- Network config ---
    udp.io.mac     := B"h00_00_01_00_00_02"
    udp.io.ip      := B"8'd10" ## B"8'd0" ## B"8'd0" ## B"8'd2"
    udp.io.gateway := B"8'd10" ## B"8'd0" ## B"8'd0" ## B"8'd1"
    udp.io.subnet  := 0

    // UDP IQ RX placeholder (kept for interface compatibility)
    val udpIqStream = Stream(Fragment(Bits(8 bits)))
    udpIqStream.ready := True   // important: provide a driver

    // ==== Fake PRN + carrier generator ====
    val fakeStream = Stream(Fragment(Bits(8 bits)))

    // Carrier NCO
    val carrierAcc = Reg(UInt(16 bits)) init(0)
    carrierAcc := carrierAcc + U(512)
    val carrier = carrierAcc.msb

    // LFSR pseudo-PRN (x^10 + x^7 + 1)
    val lfsr = Reg(UInt(10 bits)) init(U(0x3FF))
    val feedback = lfsr(9) ^ lfsr(6)
    lfsr := (lfsr(8 downto 0) ## feedback).asUInt
    val chip = lfsr(0)

    // BPSK mix → ±64
    val amp = SInt(8 bits)
    amp := Mux(carrier ^ chip, S(64, 8 bits), S(-64, 8 bits))

    fakeStream.valid := True
    fakeStream.payload.fragment := amp.asBits
    fakeStream.payload.last := False
    when(fakeStream.ready) { }  // observe ready

    // ==== Acquisition ====
    val acq = AcquisitionModular(freq_shift = 2, flush = false, debug = true)

    val (iq_stream_unfragmented, iq_availability) =
      fakeStream
        .translateInto(Stream(Bits(8 bits)))((to, from) => { to := from.fragment })
        .queueWithAvailability(100000)

    val adapter = StreamWidthAdapter(iq_stream_unfragmented, acq.io.iq)

    // Results out on UDP 1010 (rx arg wired but unused)
    val acq_results = acq.io.results.fragmentTransaction(8)
    udp.addPort(1010, acq_results, udpIqStream)


    // Counters / regs for status
    val input_counter  = Counter(32 bits, acq.io.iq.fire)
    val result_counter = Counter(32 bits, acq.io.results.fire)
    bus_ctrl.read(input_counter.value,  0x04)
    bus_ctrl.read(result_counter.value, 0x08)

    printf("Availability width: %d\n", iq_availability.getWidth)
    bus_ctrl.read(iq_availability, 0x10)
  }
}

object EthernetTestbenchVerilog extends App {
  val report = Config.spinal.generateVerilog(EthernetTestbench())
  report.mergeRTLSource("sources")
}
