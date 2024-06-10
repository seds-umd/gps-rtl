package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.com.uart.{Uart, UartCtrl, UartCtrlInitConfig, UartParityType, UartStopType}

case class UartControl(iqSize: Int = 2, baud: Int = 115200, memoryBits: Int = 1800 * 1024) extends Component {
  val io = new Bundle {
    val uart = master(Uart())
    val iq = slave Stream (Complex(iqSize))
    val spi_data = master Stream (Bits(32 bits))
  }

  val spi_word = Reg(Bits(32 bits))
  io.spi_data.payload := spi_word
  io.spi_data.valid.setAsReg() init False

  when(io.spi_data.fire) {
    io.spi_data.valid := False
  }

  val uartCtrl: UartCtrl = UartCtrl(
    config = UartCtrlInitConfig(
      baudrate = baud,
      dataLength = 8 - 1,
      parity = UartParityType.NONE,
      stop = UartStopType.ONE
    )
  )
  uartCtrl.io.uart <> io.uart
  uartCtrl.io.read.ready := False
  val uart_rx = uartCtrl.io.read

  val throw_iq = Bool()
  throw_iq := True

  val iq_bits = io.iq
    .translateInto(Stream(Bits(iqSize * 2 bits)))((to, from) => {
      to := from.asBits
    })
    .throwWhen(throw_iq)
  // Discard samples when not running

  val fifo = StreamFifo(Bits(8 bits), depth = (memoryBits / 8))
  val width_adapter = StreamWidthAdapter(iq_bits, fifo.io.push)
  fifo.io.flush := False

  val uart_gate = StreamGate(Bits(8 bits), log2Up(memoryBits / 4))
  uart_gate.io.input << fifo.io.pop
  uart_gate.io.output >> uartCtrl.io.write

  val uart_gate_config = uart_gate.io.config.clone()
  uart_gate_config >> uart_gate.io.config
  uart_gate_config.payload.setAsReg()
  uart_gate_config.valid.setAsReg() init (False)

  when(uart_gate_config.fire) {
    uart_gate_config.valid := False
  }

  val fsm = new StateMachine {
    val idle: State = new State with EntryPoint {
      whenIsActive {
        uart_rx.ready := True

        when(uart_rx.fire) {
          switch(uart_rx.payload) {
            is(M"000-----") {
              uart_gate_config.payload := (U"1" << uart_rx.payload.asUInt).resized
              uart_gate_config.valid := True
              goto(start_samples)
            }
            is(B(0x20)) {
              goto(reg_write)
            }
          }
        }
      }
    }

    val start_samples: State = new State {
      whenIsActive {
        fifo.io.flush := True

        goto(run_samples)
      }
    }

    val run_samples: State = new State {
      whenIsActive {
        throw_iq := False

        when(!uart_gate.io.running) {
          goto(idle)
        }
      }
    }

    val reg_write: State = new State {
      val byte_counter = Counter(5)
      val word = Reg(Bits(32 bits))

      onEntry {
        byte_counter.clear()
      }

      whenIsActive {
        uart_rx.ready := True
        when(uart_rx.fire) {
          byte_counter.increment()

          word := (word ## uart_rx.payload).resized
        }

        when(byte_counter === 4) {
          spi_word := word
          io.spi_data.valid := True
          goto(idle)
        }
      }
    }
  }
}

case class UartControlWrapper() extends Component {
  val io = new Bundle {
    val uart = master(Uart())
    val iq = slave Stream (Complex(2).asBits)
    val spi_data = master Stream(Bits(32 bits))
  }

  val uart_ctrl = UartControl(baud = 1000000, memoryBits = 512)
  uart_ctrl.io.uart <> io.uart
  uart_ctrl.io.iq << io.iq.translateInto(Stream(Complex(2)))((to, from) => {
    to.assignFromBits(from)
  })
  uart_ctrl.io.spi_data >> io.spi_data
}

object UartControlVerilog extends App {
  Config.spinal.generateVerilog(UartControlWrapper())
}
