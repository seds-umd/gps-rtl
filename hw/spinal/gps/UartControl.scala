package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.com.uart.{Uart, UartCtrl, UartCtrlInitConfig, UartParityType, UartStopType}

case class UartControl(iqSize: Int = 2, baud: Int = 115200, memoryBits: Int = 1800 * 1024) extends Component {
  val io = new Bundle {
    val uart = master(Uart())
    val iq = slave Stream (Complex(iqSize))
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
  uartCtrl.io.read.ready := True

  val throw_iq = Bool()
  throw_iq := True

  val iq_bits = io.iq
    .translateInto(Stream(Bits(iqSize * 2 bits)))((to, from) => {
      to := from.asBits
    })
    .throwWhen(throw_iq)
  // Discard samples when not running

  val fifo = StreamFifo(Bits(8 bits), depth = (memoryBits / 8))
  fifo.io.pop >> uartCtrl.io.write
  val width_adapter = StreamWidthAdapter(iq_bits, fifo.io.push)
  fifo.io.flush := False

  val fsm = new StateMachine {
    always {
      when(uartCtrl.io.read.fire) {
        goto(start)
      }
    }

    val start: State = new State {
      whenIsActive {
        fifo.io.flush := True

        goto(run)
      }
    }

    val run: State = new State {
      whenIsActive {
        throw_iq := False
        when(fifo.io.availability === 0) {
          goto(idle)
        }
      }
    }

    val idle: State = new State with EntryPoint {}
  }
}

case class UartControlWrapper() extends Component {
  val io = new Bundle {
    val uart = master(Uart())
    val iq = slave Stream (Complex(2).asBits)
  }

  val uart_ctrl = UartControl(baud = 1000000, memoryBits = 512)
  uart_ctrl.io.uart <> io.uart
  uart_ctrl.io.iq << io.iq.translateInto(Stream(Complex(2)))((to, from) => {
    to.assignFromBits(from)
  })
}

object UartControlVerilog extends App {
  Config.spinal.generateVerilog(UartControlWrapper())
}
