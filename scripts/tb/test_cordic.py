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
    def __init__(self, ip, input_width: int = 12, output_width: int = 9):
        super().__init__(ip, 1021)
        self.input_width = input_width
        self.output_width = output_width

    def send_xy(self, x: int, y: int, user: int = 0):
        # 31        0
        # pad y pad x

        x, y = int(x), int(y)

        assert abs(x) <= 2 ** (self.input_width - 2)
        assert abs(y) <= 2 ** (self.input_width - 2)

        if x < 0:
            x += 2**self.input_width
        if y < 0:
            y += 2**self.input_width

        data = bytearray()
        data.append(x & 0xFF)
        data.append((x >> 8) & 0xFF)
        data.append(y & 0xFF)
        data.append((y >> 8) & 0xFF)
        data.append(user)

        self.iq_stream.send(data)

    def get_angle(self):
        # 9 bit configured width, 1 sign bit, 2 integer bits - 6 data bits
        data = self.iq_stream.recv()

        angle = int.from_bytes(data[0:2], "little")
        user = data[2]

        if angle >= 2 ** (self.output_width - 1):
            angle -= 2 ** (16)  # Because of sign extension to 16 bits

        angle /= 2 ** (self.output_width - 3)

        return angle


def test_atan():
    tb = AtanTb("10.0.0.2")

    x = 0.01
    y = 1

    numbers = [0.01, 0.5, 1, -0.01, -0.5, 1]
    in_scale = 2 ** (tb.input_width - 4)

    for x in numbers:
        for y in numbers:
            ref = np.arctan2(y, x)
            tb.send_xy(int(x * in_scale), int(y * in_scale))
            time.sleep(0.001)
            actual = tb.get_angle()
            scaled = actual * np.pi
            err = np.abs(ref - scaled) / ref

            print(
                f"({x}, {y}) actual: {actual:0.3f}, scaled: {scaled:0.3f}, ref: {ref:0.3f}, err: {err:0.4f}"
            )


if __name__ == "__main__":
    # test_sincos()
    test_atan()
