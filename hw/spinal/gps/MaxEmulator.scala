package gps

import spinal.core._
import spinal.lib._

/** One synthetic satellite: a C/A code multiplied by a complex carrier. */
case class MaxEmulatorChannel() extends Bundle {
  val enable = Bool()
  val sv = UInt(6 bits) // 0 selects SV 1, as in PrnGenerator
  val code_phase = UInt(12 bits) // Code advance in samples, 0 to 4091
  val carrier_inc = UInt(32 bits) // Carrier phase step per sample, in turns / 2^32 (two's complement)
  val amplitude = UInt(8 bits)
}

case class MaxEmulatorConfig(channels: Int) extends Bundle {
  val channel = Vec(MaxEmulatorChannel(), channels)
  val noise_gain = UInt(8 bits)
  val threshold = UInt(8 bits) // Magnitude-bit threshold, in units of 128 LSBs of the internal sum
  val seed = Bits(32 bits)
}

object MaxEmulator {
  val lutBits = 6

  // Mid-step samples so the table is symmetric and never exactly zero.
  // scripts/max_emulator.py builds the same table; keep the two in step.
  // (scala.math is spelled out because spinal.lib has its own math package.)
  private def table(f: Double => Double): Seq[Int] =
    (0 until (1 << lutBits)).map(i =>
      scala.math.floor(127 * f(2 * scala.math.Pi * (i + 0.5) / (1 << lutBits)) + 0.5).toInt
    )

  def cosTable: Seq[Int] = table(scala.math.cos)
  def sinTable: Seq[Int] = table(scala.math.sin)
}

/** Stand-in for a MAX2769 front end, for board self-tests without RF hardware.
  *
  * Produces a continuous synthetic GPS L1 C/A signal (up to four satellites
  * plus optional noise), quantizes it to 2-bit I/Q and serializes it exactly
  * as MaxInterface expects: blocks of 16 samples sent as four 16-bit planes in
  * the order I-MSB, I-LSB, Q-MSB, Q-LSB, with data_sync on the first bit of
  * each plane and one sample per four clocks.
  *
  * Everything here runs in the serial clock domain. io.config may come from
  * another clock domain: it is sampled once, startDelay clocks after io.run
  * rises, so it only has to be stable from before run is raised. The first
  * block starts with the I-MSB plane, which is what MaxInterface needs after
  * reset, and sample 0 lines up with receiver timestamp 0.
  *
  * Sample n of satellite k is replica(n + code_phase) * exp(j * 2 * pi * n * carrier_inc / 2^32),
  * where replica is what PrnGenerator emits at four samples per chip. The
  * acquisition core therefore reports phase_offset = code_phase and
  * freq_offset = carrier_inc / 2^17.
  */
case class MaxEmulator(channels: Int = 2, startDelay: Int = 256) extends Component {
  require(channels >= 1 && channels <= 4)
  require(startDelay >= 2)

  val io = new Bundle {
    val run = in Bool () // Synchronous to this clock domain. Low returns to idle.
    val config = in(MaxEmulatorConfig(channels))

    // MAX2769-style serial output
    val data_out = out UInt (1 bit)
    val data_sync = out Bool ()

    // The same samples before serialization, for simulation checks
    val sample = master Flow (Complex(2))
  }

  object State extends SpinalEnum {
    val idle, delay, latch, load, preroll, running = newElement()
  }

  val state = RegInit(State.idle)
  val delay_count = Reg(UInt(log2Up(startDelay) bits)) init 0
  val tick = Reg(UInt(2 bits)) init 0
  val strobe = (state === State.running) && (tick === 0)

  // Sampled once per run. The source may sit in another clock domain.
  val cfg = Reg(MaxEmulatorConfig(channels))
  cfg.addTag(crossClockDomain)

  val cos_rom = Vec(MaxEmulator.cosTable.map(v => S(v, 8 bits)))
  val sin_rom = Vec(MaxEmulator.sinTable.map(v => S(v, 8 bits)))

  val prn = Seq.fill(channels)(PrnGenerator())
  val preroll_left = Vec.fill(channels)(Reg(UInt(12 bits)) init 0)
  val phase = Vec.fill(channels)(Reg(UInt(32 bits)) init 0)
  val preroll_done = preroll_left.map(_ === 0).reduce(_ && _)

  // xorshift32, one step per sample, one generator each for I and Q
  def xorshift(x: Bits): Bits = {
    val a = x ^ (x |<< 13)
    val b = a ^ (a |>> 17)
    b ^ (b |<< 5)
  }
  val rng_i = Reg(Bits(32 bits)) init 1
  val rng_q = Reg(Bits(32 bits)) init 1

  // Sum of four signed bytes: roughly Gaussian, zero mean
  def noiseSum(x: Bits): SInt =
    x.subdivideIn(8 bits).map(_.asSInt.resize(11 bits)).reduce(_ + _)

  for (k <- 0 until channels) {
    prn(k).io.sv := cfg.channel(k).sv
    prn(k).io.inc := U"17'h4000" // Four samples per chip
    prn(k).io.set := state === State.load
    prn(k).io.code.ready := strobe || ((state === State.preroll) && (preroll_left(k) =/= 0))
  }

  // Stage 0: look up carriers, capture code bits and noise
  val s0_valid = RegNext(strobe) init False
  val s0_cos = Vec.fill(channels)(Reg(SInt(8 bits)))
  val s0_sin = Vec.fill(channels)(Reg(SInt(8 bits)))
  val s0_code = Vec.fill(channels)(Reg(Bool()))
  val s0_noise_i = Reg(SInt(11 bits))
  val s0_noise_q = Reg(SInt(11 bits))

  when(strobe) {
    for (k <- 0 until channels) {
      val index = phase(k)(31 downto 32 - MaxEmulator.lutBits)
      s0_cos(k) := cos_rom(index)
      s0_sin(k) := sin_rom(index)
      s0_code(k) := prn(k).io.code.payload
      phase(k) := phase(k) + cfg.channel(k).carrier_inc
    }
    s0_noise_i := noiseSum(rng_i)
    s0_noise_q := noiseSum(rng_q)
    rng_i := xorshift(rng_i)
    rng_q := xorshift(rng_q)
  }

  // Stage 1: scale, sum, quantize
  val sumWidth = 21
  def term(k: Int, lut: SInt): SInt = {
    val product = (False ## cfg.channel(k).amplitude).asSInt * lut
    val signed = Mux(s0_code(k), product, -product)
    Mux(cfg.channel(k).enable, signed, S(0, product.getWidth bits)).resize(sumWidth bits)
  }
  def noiseTerm(n: SInt): SInt = (n * (False ## cfg.noise_gain).asSInt).resize(sumWidth bits)

  val v_i = (0 until channels).map(k => term(k, s0_cos(k))).reduce(_ + _) + noiseTerm(s0_noise_i)
  val v_q = (0 until channels).map(k => term(k, s0_sin(k))).reduce(_ + _) + noiseTerm(s0_noise_q)

  // Two-bit code read as two's complement stands for levels -1.5, -0.5, 0.5, 1.5
  val threshold = (cfg.threshold << 7).resize(sumWidth bits).asSInt
  def quantize(v: SInt): Bits = {
    val sign = v.msb
    val magnitude = (v >= threshold) || (v < -threshold)
    sign ## (sign ^ magnitude)
  }
  val q_i = quantize(v_i)
  val q_q = quantize(v_q)

  io.sample.valid := s0_valid
  io.sample.payload.re := q_i.asSInt
  io.sample.payload.im := q_q.asSInt

  // Serializer: collect 16 samples as four bit planes, then shift them out
  // while the next 16 are being collected.
  val sample_index = Reg(UInt(4 bits)) init 0
  val fill = Vec.fill(4)(Reg(Bits(16 bits)) init 0)
  val out_planes = Vec.fill(4)(Reg(Bits(16 bits)) init 0)
  val ser_count = Reg(UInt(6 bits)) init 0
  val ser_active = Reg(Bool()) init False
  val data_out_reg = Reg(Bool()) init False
  val data_sync_reg = Reg(Bool()) init False

  io.data_out := data_out_reg.asUInt
  io.data_sync := data_sync_reg

  data_out_reg := False
  data_sync_reg := False

  when(ser_active) {
    val plane = ser_count(5 downto 4)
    val bit = ser_count(3 downto 0)
    data_out_reg := out_planes(plane)(bit)
    data_sync_reg := bit === 0
    ser_count := ser_count + 1
  }

  when(s0_valid) {
    val bits = Vec(q_i(1), q_i(0), q_q(1), q_q(0)) // I-MSB, I-LSB, Q-MSB, Q-LSB
    val completed = Vec(Bits(16 bits), 4)
    for (p <- 0 until 4) {
      completed(p) := fill(p)
      completed(p)(sample_index) := bits(p)
      fill(p) := completed(p)
    }
    sample_index := sample_index + 1

    // Exactly one load every 64 clocks, so the bit stream has no gaps.
    when(sample_index === 15) {
      out_planes := completed
      ser_count := 0
      ser_active := True
    }
  }

  switch(state) {
    is(State.idle) {
      when(io.run) {
        delay_count := 0
        state := State.delay
      }
    }
    is(State.delay) {
      delay_count := delay_count + 1
      when(delay_count === startDelay - 1) {
        state := State.latch
      }
    }
    is(State.latch) {
      cfg := io.config
      state := State.load
    }
    is(State.load) {
      for (k <- 0 until channels) {
        preroll_left(k) := cfg.channel(k).code_phase
        phase(k) := 0
      }
      // xorshift must not start at zero
      rng_i := cfg.seed(31 downto 1) ## True
      rng_q := (cfg.seed ^ B"32'h9E3779B9") (31 downto 1) ## True
      state := State.preroll
    }
    is(State.preroll) {
      for (k <- 0 until channels) {
        when(preroll_left(k) =/= 0) {
          preroll_left(k) := preroll_left(k) - 1
        }
      }
      when(preroll_done) {
        tick := 0
        state := State.running
      }
    }
    is(State.running) {
      tick := tick + 1
    }
  }

  when(!io.run) {
    state := State.idle
    s0_valid := False
    sample_index := 0
    ser_active := False
  }
}

/** MaxEmulator wired straight into MaxInterface, to check the two agree on the serial format. */
case class MaxEmulatorLoopback(channels: Int = 2) extends Component {
  val io = new Bundle {
    val clk_ser = in Bool ()
    val run = in Bool () // Synchronous to clk_ser
    val config = in(MaxEmulatorConfig(channels))

    val iq = master Stream (ComplexTimestamp(2, 4092))
    val overflow = out Bool ()
    val sample = master Flow (Complex(2)) // In the clk_ser domain
  }

  val ser_domain = ClockDomain(io.clk_ser, ClockDomain.current.readResetWire)
  val ser_area = new ClockingArea(ser_domain) {
    val emulator = MaxEmulator(channels, startDelay = 16)
    emulator.io.run := io.run
    emulator.io.config := io.config
    io.sample << emulator.io.sample
  }

  val max = MaxInterface(iq_size = 2, period = 4092)
  max.io.clk_ser := io.clk_ser
  max.io.data_in := ser_area.emulator.io.data_out
  max.io.data_sync := ser_area.emulator.io.data_sync
  max.io.time_sync := False
  io.iq << max.io.iq
  io.overflow := max.io.overflow
}

object MaxEmulatorVerilog extends App {
  Config.spinal.generateVerilog(MaxEmulatorLoopback())
}
