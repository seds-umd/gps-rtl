package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._

case class RegConfig(
    regBits: Int = 28,
    addrBits: Int = 4,
    regVals: List[Tuple2[Int, Int]] = List(
      // Set default values
      (0, 0xa2951a3),
      (1, 0x8550488),
      (2, 0xeafe1dc),
      (3, 0x9ec0008),
      (4, 0x0c00080),
      (5, 0x8000070),
      (6, 0x8000000),
      (7, 0x400400b),

      // Stop and restart streaming
      (2, 0xe6ffbf2),
      (2, 0xe6ffdf2)
    )
)

case class MaxSpiConfig(div: Int = 100, config: RegConfig = RegConfig(), prog_defaults: Boolean = true) extends Component {
  val io = new Bundle {
    val spi = master(SpiBundle())
    val data = slave Stream(Bits(32 bits))
  }

  io.data.ready := False

  val spi_phy = MaxSpiPhy(div = div)
  spi_phy.io.spi >> io.spi
  val spi_in = spi_phy.io.data.clone()
  spi_phy.io.data << spi_in
  spi_in.valid := False
  spi_in.payload.setAsReg()
  spi_in.valid.setAsReg()

  val reg_fsm = new StateMachine {
    val reg_states = List.fill(config.regVals.length)(new State)

    val init: State = new State with EntryPoint {
      whenIsActive {
        if (prog_defaults) {
          goto(reg_states(0))
        } else {
          goto(done)
        }
      }
    }

    for (i <- 0 to (reg_states.length - 1)) {
      reg_states(i)
        .whenIsActive {
          spi_in.valid := True
          spi_in.payload := B(config.regVals(i)._2, 28 bits) ## B(config.regVals(i)._1, 4 bits)

          when(spi_in.fire) {
            if (i < (reg_states.length - 1)) {
              goto(reg_states(i + 1))
            } else {
              goto(done)
            }
          }
        }
    }

    val done: State = new State {
      whenIsActive {
        when(spi_in.ready) {
          io.data.ready := True
        }

        when(io.data.valid) {
          spi_in.valid := True
          spi_in.payload := io.data.payload
        }
      }
    }
  }
}

object MaxSpiConfigVerilog extends App {
  Config.spinal.generateVerilog(MaxSpiConfig(div = 20))
}
