import time

import adi
import numpy as np
from gps import prn_gen, rust


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
        self.sdr.tx_destroy_buffer()
        samples = prn_gen.sample(sv, self.fs, int(self.fs / 100))
        samples *= 2**14
        self.sdr.tx(samples)

    def tx_gps(self, count=8):
        self.sdr.tx_destroy_buffer()
        configs = rust.sim.random_config(count, 1, 10e3)
        samples = rust.sim.generate_signal(self.fs, int(self.fs / 10), configs)
        samples *= 2**14
        self.sdr.tx(samples)

        return configs

    def tx_tone(self, freq):
        self.sdr.tx_lo = int(freq)
        self.sdr.tx_destroy_buffer()
        samples = np.ones(int(self.fs / 100), dtype=np.complex64)
        samples *= 2**14
        self.sdr.tx(samples)

    def tx_data(self, freq, bw=0.5):
        self.sdr.tx_lo = int(freq)
        self.sdr.tx_destroy_buffer()

        x = np.random.randint(0, 2, int(self.fs / 10 * bw))
        x = x * 2 - 1
        x = np.repeat(x, int(1 / bw)).astype(np.complex64)
        x *= 2**14
        self.sdr.tx(x)


if __name__ == "__main__":
    sdr = Sdr()
    sdr.configure(fs=4.092e6, gain=-30)

    sdr.tx_prn(3)
    while True:
        time.sleep(1)
