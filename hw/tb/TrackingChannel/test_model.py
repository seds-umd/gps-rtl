import tracking_model

import numpy as np
import time


def test_sincos(count: int = 10000):
    config = tracking_model.Config()

    phases = np.random.randint(0, 2 ** (config.sincos_phase_width - 2), count)
    y = []

    start = time.time()

    for phase in phases:
        y.append(tracking_model.cordic_sin_cos(config, phase))

    end = time.time()
    avg_time = (end - start) / count * 1e6

    ref = np.exp(2j * np.pi * phases / 2 ** (config.sincos_phase_width - 2))
    ref *= 2 ** (config.sincos_out_width - 2)

    y = np.array(y)
    y = y[:, 0] + 1j * y[:, 1]
    err = np.abs(y - ref)
    err /= 2 ** (config.sincos_out_width - 2)

    assert np.mean(err) < 1e-4

    print(f"SinCos: {avg_time:0.3f} us")


def test_mixer(count: int = 10000):
    config = tracking_model.Config()
    inputs = np.random.randint(
        -(2 ** (config.mixer_width - 1)), 2 ** (config.mixer_width - 1), (count, 4)
    )

    y = []

    start = time.time()

    for x in inputs:
        y.append(tracking_model.mixer(config, x[0], x[1], x[2], x[3]))

    end = time.time()
    avg_time = (end - start) / count * 1e6

    y = np.array(y)
    y = y[:, 0] + 1j * y[:, 1]

    ref = (
        (inputs[:, 0] + 1j * inputs[:, 1])
        * (inputs[:, 2] + 1j * inputs[:, 3])
        / 2**config.mixer_width
    )

    print(f"Mixer: {avg_time:0.3f} us, avg error: {np.mean(np.abs(ref - y)):0.3f} LSB")


if __name__ == "__main__":
    test_sincos()
    test_mixer()
