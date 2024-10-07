package gps

import spinal.core._
import spinal.lib._
import ethernet._
import ethernet.stream.UdpStream

case class EthDecimate(out_size: Int = 64) extends Component {
  val io = new Bundle {
    val rx = slave Stream(Fragment(Bits(8 bits)))
    val tx = master Stream(Fragment(Bits(8 bits)))
  }

  val dut = Decimate(iq_size = 8, factor = 8)

  val rx_16b = Stream(Fragment(Bits(16 bits)))
  val rx_adapter = StreamFragmentWidthAdapter(io.rx, rx_16b)
  dut.io.iq_in << rx_16b.translateInto(Stream(Bits(16 bits)))((to, from) => {
    to := from.fragment
  })

  val tx_16b = dut.io.iq_out.addFragmentLast(Counter(out_size))
  val tx_adapter = StreamFragmentWidthAdapter(tx_16b, io.tx)
}

case class EthernetTestbench() extends Component {
  val io = new Bundle {
    val gtx_clk = in Bool ()
    val gtx_rst = in Bool ()

    val gmii = slave(GMII())
  }

  val udp = UdpStream(false)

  udp.io.gtx_clk := io.gtx_clk
  udp.io.gtx_rst := io.gtx_rst
  udp.io.gmii <> io.gmii

  udp.io.mac := B"h00_00_01_00_00_02"
  udp.io.ip := B"8'd10" ## B"8'd0" ## B"8'd0" ## B"8'd2"
  udp.io.gateway := B"8'd10" ## B"8'd0" ## B"8'd0" ## B"8'd1"
  udp.io.subnet := 0

  val decimate = EthDecimate(out_size = 4096/8)
  udp.addPort(1000, decimate.io.tx, decimate.io.rx)
}

object EthernetTestbenchVerilog extends App {
  val report = Config.spinal.generateVerilog(EthernetTestbench())
  report.mergeRTLSource("sources")
}
