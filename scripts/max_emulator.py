"""Bit-exact Python model of hw/spinal/gps/MaxEmulator.scala.

Used by the MaxEmulator and GpsSelfTest testbenches and by the board self-test
host script, so the simulation and the hardware are checked against the same
reference. Keep it in step with the Scala source.
"""

from dataclasses import dataclass
import math
from typing import List, Sequence, Tuple

import numpy as np

LUT_BITS = 6
COS_TABLE = [math.floor(127 * math.cos(2 * math.pi * (i + 0.5) / (1 << LUT_BITS)) + 0.5) for i in range(1 << LUT_BITS)]
SIN_TABLE = [math.floor(127 * math.sin(2 * math.pi * (i + 0.5) / (1 << LUT_BITS)) + 0.5) for i in range(1 << LUT_BITS)]

SAMPLE_RATE = 4.092e6  # Samples per second the acquisition core assumes
PERIOD = 4092  # Samples per C/A code period
FINE_BIN_HZ = SAMPLE_RATE / (4096 * 8)  # Unit of the core's freq_offset result
INC_PER_FINE_BIN = 1 << 17  # carrier_inc that moves the carrier by one fine bin


@dataclass
class Channel:
    """One synthetic satellite."""

    sv: int  # 1 to 32
    code_phase: int = 0  # Code advance in samples, 0 to 4091
    carrier_inc: int = 0  # Signed phase step per sample, turns / 2^32
    amplitude: int = 96
    enable: bool = True

    @property
    def doppler_hz(self) -> float:
        return self.carrier_inc * SAMPLE_RATE / 2**32

    @property
    def expected_freq_offset(self) -> float:
        """What the core's freq_offset should report, in fine bins."""
        return self.carrier_inc / INC_PER_FINE_BIN


def inc_for_fine_bin(fine_bin: int) -> int:
    """carrier_inc that puts the carrier exactly on a fine acquisition bin."""
    return fine_bin * INC_PER_FINE_BIN


def xorshift32(x: int) -> int:
    x ^= (x << 13) & 0xFFFFFFFF
    x ^= x >> 17
    x ^= (x << 5) & 0xFFFFFFFF
    return x


def _noise_sum(x: int) -> int:
    total = 0
    for shift in (0, 8, 16, 24):
        byte = (x >> shift) & 0xFF
        total += byte - 256 if byte >= 128 else byte
    return total


def noise_sequences(seed: int, count: int) -> Tuple[np.ndarray, np.ndarray]:
    """The I and Q noise sums the emulator uses for samples 0 to count-1."""
    seed &= 0xFFFFFFFF
    x_i = seed | 1
    x_q = (seed ^ 0x9E3779B9) | 1
    noise_i = np.empty(count, dtype=np.int64)
    noise_q = np.empty(count, dtype=np.int64)
    for n in range(count):
        noise_i[n] = _noise_sum(x_i)
        noise_q[n] = _noise_sum(x_q)
        x_i = xorshift32(x_i)
        x_q = xorshift32(x_q)
    return noise_i, noise_q


def replica(sv: int, count: int, advance: int = 0) -> np.ndarray:
    """C/A code as PrnGenerator emits it at four samples per chip, as +1/-1.

    Chips change two samples into each group of four, matching the half-chip
    start of the generator's phase accumulator.
    """
    from gps import prn_gen  # gps-model; only needed to generate samples

    chips = np.array(prn_gen.generate(sv), dtype=np.int64)
    n = np.arange(count, dtype=np.int64) + advance
    return chips[((n + 2) // 4) % 1023]


def _quantize(v: np.ndarray, threshold: int) -> np.ndarray:
    limit = (threshold & 0xFF) << 7
    sign = v < 0
    magnitude = (v >= limit) | (v < -limit)
    # Two's complement of {sign, sign ^ magnitude}
    return np.where(sign, -2, 0) + (sign ^ magnitude).astype(np.int64)


def samples(
    channels: Sequence[Channel],
    count: int,
    noise_gain: int = 0,
    threshold: int = 64,
    seed: int = 0,
) -> Tuple[np.ndarray, np.ndarray]:
    """2-bit I and Q codes (-2 to 1) for samples 0 to count-1 after start-up."""
    n = np.arange(count, dtype=np.uint64)
    v_i = np.zeros(count, dtype=np.int64)
    v_q = np.zeros(count, dtype=np.int64)
    cos_table = np.array(COS_TABLE, dtype=np.int64)
    sin_table = np.array(SIN_TABLE, dtype=np.int64)

    for channel in channels:
        if not channel.enable:
            continue
        inc = np.uint64(channel.carrier_inc & 0xFFFFFFFF)
        phase = (n * inc) & np.uint64(0xFFFFFFFF)
        index = (phase >> np.uint64(32 - LUT_BITS)).astype(np.int64)
        code = replica(channel.sv, count, channel.code_phase)
        v_i += channel.amplitude * cos_table[index] * code
        v_q += channel.amplitude * sin_table[index] * code

    if noise_gain:
        noise_i, noise_q = noise_sequences(seed, count)
        v_i += noise_i * noise_gain
        v_q += noise_q * noise_gain

    return _quantize(v_i, threshold), _quantize(v_q, threshold)


def to_complex(i: np.ndarray, q: np.ndarray) -> np.ndarray:
    """Map 2-bit codes to their levels: -1.5, -0.5, 0.5, 1.5."""
    return (np.asarray(i) + 0.5) + 1j * (np.asarray(q) + 0.5)


def serial_bits(i: np.ndarray, q: np.ndarray) -> List[Tuple[int, int]]:
    """(data, data_sync) pairs for whole 16-sample blocks, in transmit order."""
    out = []
    count = len(i) - len(i) % 16
    for start in range(0, count, 16):
        block_i = [int(x) & 3 for x in i[start : start + 16]]
        block_q = [int(x) & 3 for x in q[start : start + 16]]
        for plane in (
            [(x >> 1) & 1 for x in block_i],
            [x & 1 for x in block_i],
            [(x >> 1) & 1 for x in block_q],
            [x & 1 for x in block_q],
        ):
            out.extend((bit, int(j == 0)) for j, bit in enumerate(plane))
    return out
