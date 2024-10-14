package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

case class SpiBundle() extends Bundle with IMasterSlave {
  val cs = Bool()
  val sclk = Bool()
  val sdata = Bool()

  override def asMaster(): Unit = {
    out(cs, sclk, sdata)
  }

  def connectFrom(that: SpiBundle): SpiBundle = {
    this.cs := that.cs
    this.sclk := that.sclk
    this.sdata := that.sdata
    that
  }

  def <<(that: SpiBundle): SpiBundle = connectFrom(that)

  def >>(into: SpiBundle): SpiBundle = {
    into << this
    into
  }
}

case class MaxSpiPhy(div: Int = 100) extends Component {
  val io = new Bundle {
    val spi = master(SpiBundle())
    val data = slave Stream (Bits(32 bits))
  }

  io.spi.sclk := False
  io.spi.cs.setAsReg()
  io.spi.sdata.setAsReg()

  io.data.ready := False

  val current_data = Reg(Bits(32 bits))

  val spi_fsm = new StateMachine {
    val div_counter = Counter(div)

    val init: State = new State with EntryPoint {
      whenIsActive {
        div_counter.clear()

        io.spi.cs := True
        io.data.ready := True

        when(io.data.fire) {
          current_data := io.data.payload
          goto(run)
          io.spi.cs := False
        }
      }
    }

    val run: State = new State {
      val bit = Counter(32)

      whenIsActive {
        io.spi.sclk := div_counter > (div / 2).toInt
        div_counter.increment()

        when(div_counter === 0) {
          io.spi.sdata := current_data(31 - bit.value)
        }
        
        when(div_counter.willOverflow) {
          bit.increment()
        }

        when(bit.willOverflow) {
          goto(cooldown)
        }
      }
    }

    val cooldown: State = new StateDelay(cyclesCount = div) {
      whenIsActive {
        io.spi.cs := True
        io.spi.sdata := False
      }
      whenCompleted {
        goto(init)
      }
    }
  }
}

object MaxSpiPhyVerilog extends App {
  Config.spinal.generateVerilog(MaxSpiPhy(div = 20))
}
