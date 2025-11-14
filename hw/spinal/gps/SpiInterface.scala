
package gps
import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.bus.bram._


case class SpiInterface() extends Component {
    implicit val systemClockDomain = ClockDomain.current
    val io = new Bundle {
      val sclk = in Bool()
      val mosi = in Bool()
      val cs = in Bool()
      val reset = in Bool()
      val bramBus = slave(BRAM(BramBusConfig(addressWidth=15, dataWidth=16)))
      val miso = out Bool()

    }

    val cmdReg = Reg(UInt(16 bits)) init(0)
    val dataReg = Reg(UInt(16 bits)) init(0)
    val counter1 = Reg(UInt(5 bits)) init(0)
    val counter2 = Reg(UInt(5 bits)) init(0)
    val mosiReg = Reg(UInt(16 bits)) init(0)
    val readReg = Reg(UInt(16 bits)) init(0)
    val sync_sclk = BufferCC(io.sclk, True)
    val sync_mosi = BufferCC(io.mosi, False).asUInt
    val sync_cs = BufferCC(io.cs, True)
    val misoReg = Reg(Bool())

    io.miso := misoReg

    val memory = Mem(UInt(16 bits), wordCount = 32000)
    val bramWriteEnable = Reg(Bool()) init(False)
    val bramWriteAddress = Reg(UInt(15 bits)) init(0)
    val bramWriteData = Reg(UInt(16 bits)) init(0)
    val bramReadAddress = Reg(UInt(15 bits)) init(0)
    val bramReadData = UInt(16 bits) 
 

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
    

    val reg_fsm = new StateMachine {
      val init: State = new State with EntryPoint {
        onEntry{
          counter1:=0
          counter2:=0
          mosiReg:=0
          dataReg:=0
        }
        whenIsActive{
          when(sync_cs === False){
            when(sync_sclk.rise()){
              goto(get_cmd)
            }
          }
        }
      }

      val get_cmd: State = new State {
        whenIsActive{
          when(sync_sclk.fall()){
            mosiReg := (mosiReg |<< 1 ) + sync_mosi
            counter1 := counter1 + 1
            when(counter1 === 16){
              cmdReg:=mosiReg
              when(mosiReg(15)){
                goto(gap)
              } otherwise{
                goto(write)
              }
            }
          }
        }
        
      }

      val gap: State = new State {
        onEntry{
          counter2 := counter2 +1
          bramReadAddress := cmdReg(14 downto 0)
        }
        whenIsActive{
          when(sync_sclk.fall()){
            counter2 := counter2 + 1
            when(counter2 === 7){
              goto(read)
            }
          }
        }
        
      }

      val write: State = new State {
        onEntry{
          dataReg := (dataReg |<< 1 ) + sync_mosi
          counter2 := counter2 + 1
     
        }
        whenIsActive{
          when(sync_sclk.fall()){
            dataReg := (dataReg |<< 1 ) + sync_mosi
            counter2 := counter2 + 1
            when(counter2 === 16){
              bramWriteEnable := True
              bramWriteAddress := cmdReg(14 downto 0)
              bramWriteData := dataReg
              goto(init)
            }
          }
        }

""" When should I disable bramWriteEnable"""

      }

      val read: State = new State {
          onEntry{
            counter2 := 0
            readReg := bramReadData
          }
          whenIsActive{
            when(sync_sclk.rise()){
              misoReg := readReg(15)
              readReg := (readReg |<< 1 )
              """ should i send the most significant bit first or not? """
              counter2 := counter2 +1
            }
            when(counter2 === 16){
               goto(init)
            }
          }
      }

    }
  
}





object SpiInterfaceVerilog extends App {
  Config.spinal.generateVerilog(SpiInterface())
}




