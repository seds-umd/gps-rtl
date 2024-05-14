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

case class MaxSpiConfig(div: Int = 100, config: RegConfig = RegConfig()) extends Component {
  val io = new Bundle {
    val sclk = out Bool ()
    val cs = out Bool ()
    val sdata = out Bool ()
  }

  io.sclk := False
  io.cs := True
  io.sdata := False

  val addr = UInt(config.addrBits bits)
  val data = UInt(config.regBits bits)
  val start = Bool()
  val transfer_done = Bool()
  addr := 0
  data := 0
  start := False
  transfer_done := False

  val spi_fsm = new StateMachine {
    val div_counter = Counter(div)

    val init: State = new State with EntryPoint {
      whenIsActive {
        div_counter.clear()

        when(start) {
          goto(run)
          io.cs := False
        }
      }
    }

    val run: State = new State {
      val bit = Counter(config.addrBits + config.regBits)

      onEntry {
        bit.clear()
      }

      whenIsActive {
        io.cs := False
        io.sclk := div_counter > (div / 2).toInt

        div_counter.increment()

        when(div_counter.willOverflow) {
          bit.increment()

          when(bit < config.regBits) {
            // Send data
            io.sdata := data(config.regBits - bit.value)
          } otherwise {
            // Send address
            io.sdata := addr((config.addrBits - (bit.value - config.regBits)).resized)
          }
        }

        when(bit.willOverflow) {
          transfer_done := True
          goto(init)
        }
      }
    }
  }

  val reg_fsm = new StateMachine {
    val reg_states = List.fill(config.regVals.length)(new State)

    val init: State = new State with EntryPoint {
      whenIsActive {
        goto(reg_states(0))
      }
    }

    for (i <- 0 to (reg_states.length - 1)) {
      reg_states(i)
        .onEntry {
          start := True
        }
        .whenIsActive {
          addr := config.regVals(i)._1
          data := config.regVals(i)._2

          when(transfer_done) {
            if (i < (reg_states.length - 1)) {
              goto(reg_states(i + 1))
            } else {
              goto(done)
            }
          }
        }
    }

    val done: State = new State {}
  }
}

object MaxSpiConfigVerilog extends App {
  Config.spinal.generateVerilog(MaxSpiConfig())
}
