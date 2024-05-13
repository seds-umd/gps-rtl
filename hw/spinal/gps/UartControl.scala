package gps

import spinal.core._
import spinal.lib._
import spinal.lib.fsm._
import spinal.lib.com.uart.{Uart, UartCtrl, UartCtrlInitConfig, UartParityType, UartStopType}

case class UartControl(iqSize: Int = 2) extends Component {
  val io = new Bundle {
    val uart = master(Uart())
    val iq = slave Stream (Complex(iqSize))
  }

  val uartCtrl: UartCtrl = UartCtrl(
    config = UartCtrlInitConfig(
      baudrate = 115200,
      dataLength = 8 - 1,
      parity = UartParityType.NONE,
      stop = UartStopType.ONE
    )
  )
  uartCtrl.io.uart <> io.uart
	uartCtrl.io.read.ready := True

  val iq_bits = io.iq.translateInto(Stream(Bits(iqSize * 2 bits)))((to, from) => {
    to := from.asBits
  }).toFlow.toStream
  // Convert to flow and back to prevent stale samples from sitting in FIFO

  val fifo = StreamFifo(Bits(8 bits), depth = (1.8e6 / 8).toInt)
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
      }
    }

    val run: State = new State {
      whenIsActive {
        when(fifo.io.availability === 0) {
          goto(idle)
        }
      }
    }

    val idle: State = new State with EntryPoint {}
  }
}
