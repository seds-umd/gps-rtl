package gps
import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.bus.bram._

case class BramBusConfig(
  addressWidth: Int,
  dataWidth: Int
)

case class BRAM(config: BramBusConfig) extends Bundle with IMasterSlave {
  val en     = Bool()
  val we     = Bool()
  val addr   = UInt(config.addressWidth bits)
  val wrdata = UInt(config.dataWidth bits)
  val rddata = UInt(config.dataWidth bits)

  override def asMaster(): Unit = {
    out(en, we, addr, wrdata)
    in(rddata)
  }
}

case class BramTest() extends Component {
    implicit val systemClockDomain = ClockDomain.current
    val io = new Bundle {
      val w_address = in UInt(15 bits)
      val w_enable = in Bool()
      val w_data = in UInt(16 bits)
      val r_address = in UInt(15 bits)
      val r_data = out UInt(16 bits)
      val reset = in Bool()
      val bramBus = slave(BRAM(BramBusConfig(addressWidth=15, dataWidth=16)))
      val miso = out Bool()
    }


    val memory = Mem(UInt(16 bits), wordCount = 32000)
    val bramWriteEnable = Reg(Bool()) init(False)
    val bramWriteAddress = Reg(UInt(15 bits)) init(0)
    val bramWriteData = Reg(UInt(16 bits)) init(0)
    val bramReadAddress = Reg(UInt(15 bits)) init(0)
    val bramReadData = UInt(16 bits) 


    io.miso := True;

    memory.write(
    enable = bramWriteEnable,
    address = bramWriteAddress,
    data = bramWriteData
    ) 
    bramReadData := memory.readSync(
    address = bramReadAddress,
    enable = True
  )
  memory.write(
    enable = io.bramBus.en && io.bramBus.we,
    address = io.bramBus.addr,
    data = io.bramBus.wrdata
  )
   io.bramBus.rddata := memory.readSync(
    address = io.bramBus.addr,
    enable = io.bramBus.en && !io.bramBus.we
  )

  bramWriteAddress := io.w_address
  bramWriteEnable := io.w_enable
  bramWriteData := io.w_data
  
  bramReadAddress := io.r_address
  io.r_data := bramReadData
  

}



object BramTestVerilog extends App {
  Config.spinal.generateVerilog(BramTest())
}





































































