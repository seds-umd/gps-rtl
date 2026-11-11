package gps

import spinal.core._
import spinal.lib._
import spinal.lib.com.uart.{Uart, UartCtrl, UartCtrlInitConfig, UartParityType, UartStopType}

/** One line of text: a prefix character, up to 12 hex digits, then CR LF. */
case class HexLine() extends Bundle {
  val prefix = Bits(8 bits)
  val digits = Bits(48 bits) // Left-aligned; the first digit sent is bits 47 to 44
  val count = UInt(4 bits)
}

case class HexLineTx() extends Component {
  val io = new Bundle {
    val line = slave Stream (HexLine())
    val tx = master Stream (Bits(8 bits))
  }

  object State extends SpinalEnum {
    val idle, prefix, digits, cr, lf = newElement()
  }

  val state = RegInit(State.idle)
  val prefix = Reg(Bits(8 bits))
  val shift = Reg(Bits(48 bits))
  val left = Reg(UInt(4 bits))

  def hexChar(n: UInt): Bits = Mux(n < 10, n.resize(8 bits) + 0x30, n.resize(8 bits) + 0x37).asBits

  io.line.ready := state === State.idle
  io.tx.valid := state =/= State.idle
  io.tx.payload := prefix

  switch(state) {
    is(State.idle) {
      when(io.line.valid) {
        prefix := io.line.prefix
        shift := io.line.digits
        left := io.line.count
        state := State.prefix
      }
    }
    is(State.prefix) {
      when(io.tx.ready) {
        state := Mux(left === 0, State.cr, State.digits)
      }
    }
    is(State.digits) {
      io.tx.payload := hexChar(shift(47 downto 44).asUInt)
      when(io.tx.ready) {
        shift := shift |<< 4
        left := left - 1
        when(left === 1) {
          state := State.cr
        }
      }
    }
    is(State.cr) {
      io.tx.payload := 0x0d
      when(io.tx.ready) {
        state := State.lf
      }
    }
    is(State.lf) {
      io.tx.payload := 0x0a
      when(io.tx.ready) {
        state := State.idle
      }
    }
  }
}

object GpsSelfTest {
  val id = BigInt("47505331", 16) // "GPS1"

  // Register addresses. scripts/arty_selftest.py has the same map.
  val regCtrl = 0x00 // bit 0: run
  val regId = 0x01 // read only
  val regStatus = 0x02 // read only: bit 0 sample overflow, bits 31:8 results since run was raised
  val regQuant = 0x03 // bits 7:0 noise gain, bits 15:8 magnitude threshold
  val regSeed = 0x04
  val regInfo = 0x05 // read only: bits 7:0 channels, bits 15:8 coarse bins each side
  val regChannelBase = 0x10 // per channel: +0 control, +1 carrier increment, +2 code phase
  val regChannelStride = 4
}

/** Self-contained board test for the acquisition core.
  *
  * A MaxEmulator generates a known synthetic satellite signal on the serial
  * clock, GpsTop acquires it through the normal MAX2769 serial path and the
  * real FFT core, and each result goes to the host as one line of text on the
  * UART. The host can stop the core, reprogram the emulator and start it
  * again, so one bitstream covers any number of test signals.
  *
  * Host to board (ASCII; spaces and tabs are ignored):
  *   W aa dddddddd   write register aa         reply: w aa dddddddd (value read back)
  *   Q aa            read register aa          reply: q aa dddddddd
  *   ?               identify                  reply: i 01 47505331
  *   anything else                             reply: e
  * A command needs no terminator; CR and LF between commands are ignored. A CR
  * or LF before a command is complete cancels it with an e reply, so sending
  * a line end always brings the parser back to idle. Emulator registers can
  * only be written while stopped; writing one while running is refused with e.
  * Send the next command after the reply to the previous one.
  * Board to host, one line per acquisition result while running:
  *   R ss fff ppp mm o    satellite, freq_offset, phase_offset, metric, flags (bit 0: sample overflow)
  * Replies and results are sent without the spaces shown here.
  *
  * Write CTRL=0 before changing the emulator registers and CTRL=1 afterwards.
  * Lowering run resets GpsTop and returns the emulator to idle, so every run
  * starts from sample 0 and receiver timestamp 0.
  */
case class GpsSelfTest(freq_shift: Int = 24, channels: Int = 2, baud: Int = 115200) extends Component {
  import GpsSelfTest._

  val io = new Bundle {
    val clk_ser = in Bool () // About 16.368 MHz: four clocks per 4.092 Msps sample
    val uart = master(Uart())
    val leds = out Bits (4 bits) // heartbeat, running, strong result seen, sample overflow
  }

  // ---- Registers (system clock domain) ----
  val run = RegInit(True)

  case class ChannelRegs() extends Bundle {
    val enable = Bool()
    val sv = UInt(6 bits) // 1 to 32, as in the results
    val amplitude = UInt(8 bits)
    val carrier_inc = UInt(32 bits)
    val code_phase = UInt(12 bits)
  }

  // Power-on defaults give a visible result stream without a host: satellite 7
  // at fine bin 16 (about 2 kHz) with a code phase of 1000 samples.
  val channel_regs = Vec.tabulate(channels) { k =>
    val regs = Reg(ChannelRegs())
    regs.enable init Bool(k == 0)
    regs.sv init (if (k == 0) 7 else 19)
    regs.amplitude init 96
    regs.carrier_inc init (if (k == 0) U(16 << 17, 32 bits) else U(BigInt(0x100000000L) - (40 << 17), 32 bits))
    regs.code_phase init (if (k == 0) 1000 else 2500)
    regs
  }
  val noise_gain = Reg(UInt(8 bits)) init 0
  val threshold = Reg(UInt(8 bits)) init 64
  val seed = Reg(Bits(32 bits)) init 1

  val emulator_config = MaxEmulatorConfig(channels)
  for (k <- 0 until channels) {
    emulator_config.channel(k).enable := channel_regs(k).enable
    emulator_config.channel(k).sv := channel_regs(k).sv - 1
    emulator_config.channel(k).code_phase := channel_regs(k).code_phase
    emulator_config.channel(k).carrier_inc := channel_regs(k).carrier_inc
    emulator_config.channel(k).amplitude := channel_regs(k).amplitude
  }
  emulator_config.noise_gain := noise_gain
  emulator_config.threshold := threshold
  emulator_config.seed := seed

  // ---- Signal source (serial clock domain) ----
  val ser_domain = ClockDomain(io.clk_ser, ClockDomain.current.readResetWire)
  val ser_area = new ClockingArea(ser_domain) {
    val emulator = MaxEmulator(channels)
    emulator.io.run := BufferCC(run, init = False)
    // Sampled once, well after run rises; the host changes it only while stopped.
    emulator.io.config := emulator_config
  }

  // ---- Device under test: held in reset while stopped ----
  val core = new ResetArea(!run, cumulative = true) {
    val gps = GpsTop(freq_shift)
  }
  val gps = core.gps
  gps.io.clk_ser := io.clk_ser
  gps.io.data_in := ser_area.emulator.io.data_out
  gps.io.data_sync := ser_area.emulator.io.data_sync
  gps.io.time_sync := False

  val result_count = Reg(UInt(24 bits)) init 0
  when(gps.io.results.fire) {
    result_count := result_count + 1
  }
  when(!run) {
    result_count := 0
  }

  // ---- UART ----
  val uart_ctrl = UartCtrl(
    config = UartCtrlInitConfig(
      baudrate = baud,
      dataLength = 8 - 1,
      parity = UartParityType.NONE,
      stop = UartStopType.ONE
    )
  )
  uart_ctrl.io.uart <> io.uart

  val line_tx = HexLineTx()
  line_tx.io.tx >> uart_ctrl.io.write

  // ---- Command parser ----
  object Parser extends SpinalEnum {
    val idle, collect, execute, respond = newElement()
  }
  val parser = RegInit(Parser.idle)
  val is_write = Reg(Bool())
  val need = Reg(UInt(4 bits))
  val got = Reg(UInt(4 bits))
  val hex = Reg(Bits(40 bits))
  val reply = Reg(HexLine())
  val reply_valid = RegInit(False)
  val reply_prefix = Reg(Bits(8 bits))
  val failed = Reg(Bool())

  val rx = uart_ctrl.io.read
  rx.ready := True // The UART has no receive buffer; the parser consumes every byte as it arrives.

  val char = rx.payload.asUInt
  val is_digit = char >= 0x30 && char <= 0x39
  val is_alpha = (char >= 0x41 && char <= 0x46) || (char >= 0x61 && char <= 0x66)
  val is_line_end = char === 0x0d || char === 0x0a
  val is_space = char === 0x20 || char === 0x09
  val nibble = Mux(is_digit, char(3 downto 0), char(3 downto 0) + 9)

  val address = Mux(is_write, hex(39 downto 32), hex(7 downto 0)).asUInt
  val write_data = hex(31 downto 0)
  // The emulator samples its settings once per run, so they may only change while stopped.
  val is_emulator_register = address === regQuant || address === regSeed ||
    (address >= regChannelBase && address < regChannelBase + regChannelStride * channels)

  // Read multiplexer
  val read_data = Bits(32 bits)
  read_data := 0
  switch(address) {
    is(regCtrl) { read_data(0) := run }
    is(regId) { read_data := B(id, 32 bits) }
    is(regStatus) { read_data := result_count.asBits ## B(0, 7 bits) ## gps.io.sample_overflow }
    is(regQuant) { read_data := (threshold ## noise_gain).resized }
    is(regSeed) { read_data := seed }
    is(regInfo) { read_data := B(freq_shift, 8 bits).resize(24 bits) ## B(channels, 8 bits) }
  }
  for (k <- 0 until channels) {
    val base = regChannelBase + regChannelStride * k
    val regs = channel_regs(k)
    switch(address) {
      is(base + 0) { read_data := (regs.amplitude ## B(0, 7 bits) ## regs.enable ## B(0, 2 bits) ## regs.sv).resized }
      is(base + 1) { read_data := regs.carrier_inc.asBits }
      is(base + 2) { read_data := regs.code_phase.asBits.resized }
    }
  }

  switch(parser) {
    is(Parser.idle) {
      when(rx.valid && !is_space && !is_line_end) {
        got := 0
        failed := False
        parser := Parser.collect
        switch(char) {
          is(0x57, 0x77) { // W
            is_write := True
            need := 10
            reply_prefix := 0x77
          }
          is(0x51, 0x71) { // Q
            is_write := False
            need := 2
            reply_prefix := 0x71
          }
          is(0x3f) { // ?
            is_write := False
            hex(7 downto 0) := regId
            reply_prefix := 0x69
            parser := Parser.execute
          }
          default {
            failed := True
            parser := Parser.respond
          }
        }
      }
    }
    is(Parser.collect) {
      when(rx.valid && !is_space) {
        when((is_digit || is_alpha) && !is_line_end) {
          hex := (hex ## nibble).resized
          got := got + 1
          when(got + 1 === need) {
            parser := Parser.execute
          }
        } otherwise {
          failed := True
          parser := Parser.respond
        }
      }
    }
    is(Parser.execute) {
      when(is_write && is_emulator_register && run) {
        failed := True
      } elsewhen (is_write) {
        switch(address) {
          is(regCtrl) { run := write_data(0) }
          is(regQuant) {
            noise_gain := write_data(7 downto 0).asUInt
            threshold := write_data(15 downto 8).asUInt
          }
          is(regSeed) { seed := write_data }
        }
        for (k <- 0 until channels) {
          val base = regChannelBase + regChannelStride * k
          val regs = channel_regs(k)
          switch(address) {
            is(base + 0) {
              regs.sv := write_data(5 downto 0).asUInt
              regs.enable := write_data(8)
              regs.amplitude := write_data(23 downto 16).asUInt
            }
            is(base + 1) { regs.carrier_inc := write_data.asUInt }
            is(base + 2) { regs.code_phase := write_data(11 downto 0).asUInt }
          }
        }
      }
      parser := Parser.respond
    }
    is(Parser.respond) {
      // One cycle after execute, so a write reads back what was stored. Wait
      // for any earlier reply to be taken so that it is not overwritten.
      when(!reply_valid) {
        reply.prefix := Mux(failed, B(0x65, 8 bits), reply_prefix)
        reply.digits := address.asBits ## read_data ## B(0, 8 bits)
        reply.count := Mux(failed, U(0, 4 bits), U(10, 4 bits))
        reply_valid := True
        parser := Parser.idle
      }
    }
  }

  // ---- Result lines; command replies go first ----
  val result = gps.io.results
  val result_line = HexLine()
  result_line.prefix := 0x52 // R
  result_line.digits := B"00" ## result.sv ## result.freq_offset ## result.phase_offset ## result.snr ##
    B"000" ## gps.io.sample_overflow ## B"0000"
  result_line.count := 11

  line_tx.io.line.valid := reply_valid || result.valid
  line_tx.io.line.payload := Mux(reply_valid, reply, result_line)
  result.ready := line_tx.io.line.ready && !reply_valid
  // Placed after the parser so that it wins; respond only sets reply_valid when it is already clear.
  when(reply_valid && line_tx.io.line.ready) {
    reply_valid := False
  }

  // ---- LEDs ----
  val heartbeat = Reg(UInt(26 bits)) init 0
  heartbeat := heartbeat + 1

  // Hold the "strong result" LED for about a third of a second per detection.
  val strong_hold = Reg(UInt(24 bits)) init 0
  when(result.fire && result.snr >= 32) {
    strong_hold := strong_hold.maxValue
  } elsewhen (strong_hold =/= 0) {
    strong_hold := strong_hold - 1
  }

  io.leds := gps.io.sample_overflow ## (strong_hold =/= 0) ## run ## heartbeat.msb
}

object GpsSelfTestVerilog extends App {
  Config.spinal.generateVerilog(GpsSelfTest())
}

object GpsSelfTestSimVerilog extends App {
  // Two-bin coarse span and a fast, exactly divisible baud rate to keep simulation short.
  Config.spinal.generateVerilog(GpsSelfTest(freq_shift = 2, baud = 1250000).setDefinitionName("GpsSelfTestSim"))
}
