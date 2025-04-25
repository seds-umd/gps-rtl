import adi
import numpy as np
from gps import gps, gps_sim

fs = 4.092e6
fc = 1575.42e6

sdr = adi.Pluto("ip:192.168.20.1")

sdr.sample_rate = int(fs)
sdr.tx_rf_bandwidth = int(fs)
sdr.tx_lo = int(fc)
sdr.tx_hardwaregain_chan0 = -55 # dB
sdr.tx_destroy_buffer()

x = gps_sim.generate_gps(fs, int(1 * fs), sv=24, signal_power=None)

# for sv in [2, 8, 14, 28]:
#     x += gps_sim.generate_gps(fs, int(1 * fs), sv=sv, doppler=sv*200, sample_phase=sv*100, signal_power=None)
# x = np.fromfile("../../gps-model/data/test2.ci16", dtype=np.int8)
# x = x[::2].astype(np.complex64) + 1j * x[1::2]

x /= np.max(np.abs(x))
x *= 2**14

res = gps.acquisition(x, fs, 10e3, 500, threshold=6)
for r in res:
    print(r)

BLOCK = int(fs)

# print(len(x))

x = x[:len(x) - len(x) % BLOCK]
# print(len(x))

while True:
    print("TXing")

    for i in range(0, len(x), BLOCK):
        samples = x[i:i+BLOCK]
        # print(len(samples))
        if len(samples) > 0:
            sdr.tx(samples)
