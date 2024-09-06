package gps

import spinal.core._
import spinal.lib._
import ethernet._
import ethernet.stream.UdpStream

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

  val rx0, tx0, rx1, tx1 = Stream(Fragment(Bits(8 bits)))

  udp.addPort(100, tx0, rx0)
  udp.addPort(200, tx1, rx1)

  tx0 << rx0
  tx1 << rx1
}

object EthernetTestbenchVerilog extends App {
  val report = Config.spinal.generateVerilog(EthernetTestbench())
  report.mergeRTLSource("sources")
}
