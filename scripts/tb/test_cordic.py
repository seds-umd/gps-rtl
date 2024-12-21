import template

import numpy as np
import time
import matplotlib.pyplot as plt


class SinCosTb(template.TemplateTb):
    def __init__(self, ip):
        super().__init__(ip, 1020)

    def send_phase_int(self, phase: int, user: int = 0):
        # 12 bit phase width
        # 3 bits for integer, 9 bits for fraction
        # +1 is 001.000_000_000
        # -1 is 111.000_000_000

        # 0:1 - phase, lower bits in first byte
        # 2 - user

        phase = int(phase)

        assert phase >= 0
        assert phase < 2**12

        if phase > 2**9:
            phase = (0b111 << 10) + phase

        data = bytearray()
        data.append(phase & 0xFF)
        data.append((phase >> 8) & 0xFF)
        data.append(user)

        self.iq_stream.send(data)

    def get_complex(self):
        # 10 bit output width, x2 for re+im
        # 2 bits for integer, 8 bits for fraction
        data = self.iq_stream.recv()

        re = int.from_bytes(data[0:2], "little")
        im = int.from_bytes(data[2:4], "little")
        user = data[4]

        if re > 2**15:
            re = re - (1 << 16)

        if im > 2**15:
            im = im - (1 << 16)

        return re, im

    def do_calc_int(self, phase: int):
        self.send_phase_int(phase)
        time.sleep(0.001)
        return self.get_complex()


def test_sincos():
    tb = SinCosTb("10.0.0.2")

    t = np.linspace(0, 2**10 - 1, 200)
    y = [tb.do_calc_int(i) for i in t]
    # output range is -128 to 128
    y = np.array(y) / 128
    y = y[:, 0] + 1j * y[:, 1]

    ref = np.exp(2j * np.pi * t / 2**10)

    plt.figure(figsize=(8, 6), dpi=300)
    plt.plot(t, y.real - ref.real)
    plt.plot(t, y.imag - ref.imag)
    plt.tight_layout()
    plt.savefig("sincos.png")

    err = np.abs(y - ref)
    print(f"Error std: {np.std(err)}")


class AtanTb(template.TemplateTb):
    def __init__(self, ip, input_width: int = 12, output_width: int = 11):
        super().__init__(ip, 1021)
        self.input_width = input_width
        self.output_width = output_width

    def send_xy(self, x: int, y: int, user: int = 0):
        # 31        0
        # pad y pad x

        x, y = int(x), int(y)

        data = bytearray()
        data.extend(x.to_bytes(2, "little", signed=True))
        data.extend(y.to_bytes(2, "little", signed=True))
        data.append(user)

        self.iq_stream.send(data)

    def get_angle(self):
        # 9 bit configured width, 1 sign bit, 2 integer bits - 6 data bits
        data = self.iq_stream.recv()

        angle = int.from_bytes(data[0:2], "little", signed=True)
        # angle /= 2 ** (self.output_width - 3)
        user = data[2]

        return angle

    def compute_angle(self, x: float, y: float):
        assert -1 <= x <= 1
        assert -1 <= y <= 1

        x = int(x * 2 ** (self.input_width - 2))
        y = int(y * 2 ** (self.input_width - 2))

        self.send_xy(x, y)
        time.sleep(0.001)
        return self.get_angle()


def atan2_sim(x: int, y: int, output_width: int = 9) -> int:
    res = np.arctan2(y, x) / np.pi
    res *= 2 ** (output_width - 3)

    return int(res)


def sim_wrapper(x: float, y: float, input_width: int = 12, output_width: int = 11):
    x = int(x * 2 ** (input_width - 2))
    y = int(y * 2 ** (input_width - 2))

    res = atan2_sim(x, y, output_width)
    # res /= 2 ** (output_width - 3)

    return res


def test_atan():
    tb = AtanTb("10.0.0.2")

    numbers = [0.01, 0.5, 1, -0.01, -0.5, 1]

    fig, axs = plt.subplots(len(numbers), 2, sharex=True, figsize=(6, 8), dpi=300)

    for i, x in enumerate(numbers):
        ys = np.linspace(-1, 1, 100)
        actual = np.array([tb.compute_angle(x, y) for y in ys])
        simmed = np.array([sim_wrapper(x, y) for y in ys])
        ref = np.array([np.arctan2(y, x) for y in ys]) / np.pi

        axs[i, 0].plot(ys, actual)
        axs[i, 0].plot(ys, simmed)
        axs[i, 1].plot(ys, actual - simmed)

    plt.tight_layout()
    plt.savefig("atan2.png")


if __name__ == "__main__":
    # test_sincos()
    test_atan()
