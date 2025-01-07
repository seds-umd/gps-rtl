import numpy as np
import time
import timeit
from dataclasses import dataclass

config = {
    "cordic_phase_width": 12,
    "cordic_output_width": 9,
}


@dataclass
class Config:
    sincos_phase_width: int = 12
    sincos_out_width: int = 9
    mixer_width: int = 8


def check_width(val: int, width: int, signed: bool = False):
    if signed:
        assert val < 2 ** (width - 1), val
        assert -val <= 2 ** (width - 1), val
    else:
        assert val >= 0, val
        assert val < 2**width, val


def round_to_inf(val: int, bits: int):
    val /= 2**bits
    val = int(np.sign(val) * np.floor(np.abs(val) + 0.5))
    return val


# CordicSinCosWrapper
def cordic_sin_cos(config: Config, phase: int) -> tuple[int, int]:
    check_width(phase, config.sincos_phase_width - 2, False)

    phase = float(phase)
    phase /= 2 ** (config.sincos_phase_width - 2)

    res = np.exp(2j * np.pi * phase)
    re = res.real * 2 ** (config.sincos_out_width - 2)
    im = res.imag * 2 ** (config.sincos_out_width - 2)

    return re, im


def mixer(
    config: Config, a_re: int, a_im: int, b_re: int, b_im: int
) -> tuple[int, int]:
    check_width(a_re, config.mixer_width, True)
    check_width(a_im, config.mixer_width, True)
    check_width(b_re, config.mixer_width, True)
    check_width(b_im, config.mixer_width, True)

    out_re = a_re * b_re - a_im * b_im
    out_im = a_re * b_im + a_im * b_re
    out_re = round_to_inf(out_re, config.mixer_width)
    out_im = round_to_inf(out_im, config.mixer_width)

    return out_re, out_im


def remove_prn(config: Config):
    pass


def decimate(config: Config):
    pass


def pll(config: Config):
    pass


def cordic_atan(config: Config):
    pass


class TrackingChannel:
    def __init__(self, config):
        self.config = config

        self.inputs = list()

    def input(self, values: list):
        self.inputs.extend(values)

    def run(self):
        pass


if __name__ == "__main__":
    config = Config()

    N = int(1e5)

    total = timeit.timeit(lambda: cordic_sin_cos(config, 123), number=N)
    avg_us = total / N * 1e6

    print(f"Average time: {avg_us:0.2f} us")
