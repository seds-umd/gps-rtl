import template

import numpy as np
import time
import matplotlib.pyplot as plt


class CordicTb(template.TemplateTb):
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

        self.stream.send(data)

    def get_complex(self):
        # 10 bit output width, x2 for re+im
        # 2 bits for integer, 8 bits for fraction
        data = self.stream.recv()

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


if __name__ == "__main__":
    tb = CordicTb("10.0.0.2")

    t = np.linspace(0, 2**10 - 1, 200)
    y = [tb.do_calc_int(i) for i in t]
    # output range is -256 to 256
    y = np.array(y) / 256
    y = y[:, 0] + 1j * y[:, 1]

    ref = np.exp(2j * np.pi * t / 2**10)

    plt.figure(figsize=(8, 6), dpi=300)
    plt.plot(t, y.real - ref.real)
    plt.plot(t, y.imag - ref.imag)
    plt.tight_layout()
    plt.savefig("cordic.png")

    err = np.abs(y - ref)
    print(f"Error std: {np.std(err)}")
