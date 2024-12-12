import adi
import numpy as np
from gps import gps, gps_sim

fs = 4e6
fc = 1575.42e6 - fs * 0.2

sdr = adi.Pluto("ip:192.168.20.1")

sdr.sample_rate = int(fs)
sdr.tx_rf_bandwidth = int(fs)
sdr.tx_lo = int(fc)
sdr.tx_hardwaregain_chan0 = -50  # dB
# sdr.tx_hardwaregain_chan0 = -30 # dB
sdr.tx_destroy_buffer()

x = gps_sim.generate_gps(fs, int(1 * fs), 6, signal_power=None)
# x = np.ones(int(fs)).astype(np.complex64)

x /= np.max(np.abs(x))
x *= 2**14

print(gps.acquisition(x, fs, 10e3, 500, threshold=0)[5])

for _ in range(10):
    print("TXing")
    sdr.tx(x)
