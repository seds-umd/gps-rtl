import serial
import numpy as np
import matplotlib.pyplot as plt

from gps.gps import acquisition


# https://stackoverflow.com/a/9147327
def twos_comp(val, bits=8):
    if (val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


def normalize_iq(sample: int):
    re = sample & 0b11
    im = (sample >> 2) & 0b11

    # 0x2D bias is optimized to reduce DC offset
    re = (re << 6) | 0x2D
    im = (im << 6) | 0x2D

    re = twos_comp(re)
    im = twos_comp(im)

    c = re + im * 1j
    c /= 128

    return c


def decode_samples(data: bytearray):
    samples = []

    for b in data:
        samples.append(normalize_iq(b & 0xF))
        samples.append(normalize_iq((b >> 4) & 0xF))

    return np.array(samples)


class MaxBasys:
    def __init__(self, port, baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0.1)

    def __del__(self):
        self.ser.close()

    def get_data(self, param=8):
        # Write any data to start transfer
        self.ser.write(bytes([param]))

        data = bytearray()

        while True:
            new = self.ser.read(100)

            if len(new) == 0:
                break

            data.extend(new)

        return data

    def get_samples(self, n):
        return decode_samples(self.get_data(n - 1))


if __name__ == "__main__":
    device = MaxBasys("/dev/ttyUSB1", baud=3125 * 1000)
    samples = device.get_samples(13)
    fs = 4.092e6

    print(acquisition(samples, fs, 20e3, 500, 0, verbose=True))



    freqs = np.linspace(-fs / 2, fs / 2, len(samples))

    X = np.abs(np.fft.fftshift(np.fft.fft(samples))) / len(samples)
    X = 10*np.log10(X)

    plt.figure()
    plt.plot(freqs, X)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude (dBFS)")
    plt.tight_layout()
    plt.savefig("basys.png")
