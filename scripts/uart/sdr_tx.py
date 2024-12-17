import adi
import numpy as np
import time

from gps import prn_gen, rust, gps


def generate_chirp(fs, num, bw_ratio=0.5):
    f_0 = -fs / 2 * bw_ratio
    f_1 = fs / 2 * bw_ratio

    freq = np.linspace(f_0, f_1, int(num))
    phase = np.cumsum(freq) / fs * 2 * np.pi

    return np.exp(1j * phase)


class Sdr:
    def __init__(self, ip="ip:192.168.20.1"):
        self.sdr = adi.Pluto(ip)
        self.sdr.tx_hardwaregain_chan0 = int(-80)
        self.sdr.tx_lo = int(1575.42e6)

    def configure(self, fs=5e6, gain=-30):
        self.fs = fs
        self.gain = gain

        self.sdr.sample_rate = int(fs)
        self.sdr.tx_rf_bandwidth = int(fs)
        self.sdr.tx_hardwaregain_chan0 = int(gain)
        self.sdr.tx_cyclic_buffer = True

    def tx_prn(self, sv):
        N = int(self.fs / 10)
        t = np.arange(N) / self.fs
        samples = prn_gen.sample(sv, self.fs, N)
        samples *= np.exp(2j * np.pi * t * self.fs / 4)
        samples *= 2**13

        self.sdr.tx_lo = int(1575.42e6 - self.fs / 4)
        self.sdr.tx_destroy_buffer()
        self.sdr.tx(samples)

    def tx_gps(self, count=8):
        N = int(self.fs / 10)
        t = np.arange(N) / self.fs
        configs = rust.sim.random_config(count, 1, 10e3)
        samples = rust.sim.generate_signal(self.fs, N, configs)
        samples *= np.exp(2j * np.pi * t * self.fs / 4)
        samples *= 2**14

        self.sdr.tx_lo = int(1575.42e6 - self.fs / 4)
        self.sdr.tx_destroy_buffer()
        self.sdr.tx(samples)

        print(gps.acquisition(samples, self.fs, 15e3, 1e3))

        return configs

    def tx_tone(self, freq):
        self.sdr.tx_lo = int(freq)
        self.sdr.tx_destroy_buffer()
        samples = np.ones(int(self.fs / 100), dtype=np.complex64)
        samples *= 2**14
        self.sdr.tx(samples)

    def two_tones(self, f1: float, f2: float):
        self.sdr.tx_destroy_buffer()

        N = int(self.fs / 100)
        t = np.arange(N) / self.fs
        x1 = 0.5 * np.exp(2.0j * np.pi * f1 * t)
        x2 = 0.5 * np.exp(2.0j * np.pi * f2 * t)
        x = (x1 + x2) / 2
        x *= 2**14
        self.sdr.tx(x)

    def tx_data(self, freq, bw=0.5):
        self.sdr.tx_lo = int(freq)
        self.sdr.tx_destroy_buffer()

        x = np.random.randint(0, 2, int(self.fs / 10 * bw))
        x = x * 2 - 1
        x = np.repeat(x, int(1 / bw)).astype(np.complex64)
        x *= 2**14
        self.sdr.tx(x)

    def chirp(self, fc, bw=0.5, dur=1):
        x = generate_chirp(self.fs, dur * self.fs, bw) * 2**14

        self.sdr.tx_lo = int(fc)
        self.sdr.tx_destroy_buffer()
        self.sdr.tx(x)


if __name__ == "__main__":
    sdr = Sdr()

    # -50 dB gain is about -113 dBm actual power after 60dB attenuation
    # -65 dB gain for realistic power level
    sdr.configure(fs=4.092e6 * 2, gain=-50)
    print(f"Sample rate: {sdr.fs}")
    print(f"Gain: {sdr.gain}")

    # configs = sdr.tx_gps()

    # for c in configs:
    #     print(c)

    sdr.tx_prn(10)

    print("Transmitting")
    while True:
        time.sleep(1)
