import template
import stream

import numpy as np
import time
import random

from gps.gps import acquisition


class AcquisitionTestbench(template.TemplateTb):
    def __init__(self, ip):
        super().__init__(ip, 1010)

        self.csr_stream = stream.AxilInterface(ip, 1000)
        self.reset()
        time.sleep(0.1)

    def reset(self):
        self.csr_stream.write(0x00, 0)

    def send_file(self, file, dtype, count: int):
        data = np.fromfile(file, dtype=dtype, count=int(count))

        samples = data[::2].astype(np.complex64) + 1j * data[1::2].astype(np.complex64)

        self.send_samples(samples)

    def send_samples(self, samples):
        # Normalize - scaling optimized for SNR
        samples /= np.max(np.abs(samples))
        samples *= 127

        # Repeat
        times_single = np.arange(4092)
        times = np.tile(times_single, int(len(samples) / 4092) + 1)
        times = times.astype(np.uint16)[0 : len(samples)]

        # Convert to 4 bit format
        samples_re = samples.real.astype(np.int8).astype(np.uint8) >> 6
        samples_im = samples.imag.astype(np.int8).astype(np.uint8) >> 6
        bits = samples_re | (samples_im << 2) | (times << 4)
        bits = np.array(bits, dtype=np.uint16)

        # Get quantized samples
        samples_re = (samples_re << 6).astype(np.int8) | 0b100000
        samples_im = (samples_im << 6).astype(np.int8) | 0b100000

        samples_quant = samples_re + samples_im * 1j
        samples_quant /= 128

        # SpinalHDL width adapter puts lower bits in first
        bits_bytes = np.empty(len(bits) * 2, dtype=np.uint8)
        bits_bytes[::2] = bits & 0xFF
        bits_bytes[1::2] = bits >> 8

        self.stream.send(bits_bytes)
        self.samples_quant = samples_quant

    def get_results(self):
        res_bytes = self.stream.recv()
        res_bytes.reverse()

        res_int = 0
        res = {}

        for i in range(len(res_bytes)):
            res_int |= res_bytes[i]
            res_int <<= 8

        # Discard padding byte
        res_int >>= 8

        # Order is opposite of
        res["sv"] = res_int & 0x3F
        res_int >>= 6

        res["freq"] = res_int & 0xFFF
        res_int >>= 12

        res["phase"] = res_int & 0xFFF
        res_int >>= 12

        res["snr"] = res_int & 0xFF
        res_int >>= 8

        return res


if __name__ == "__main__":
    tb = AcquisitionTestbench("10.0.0.2")

    # N = 4096 * 9 * 8 * 32
    N = 4.092e6 * 0.6

    samples = np.ones(int(N), dtype=np.complex64)

    for _ in range(100):
        tb.csr_stream.write(0x10, 0xF0)

    print(f"Input count: {tb.csr_stream.read(0x04)}")
    print(f"Result count: {tb.csr_stream.read(0x08)}")

    print("Sending samples")
    # tb.send_file("../../../gps-model/data/1/gpssim.ci16", np.int8, 4096*9*8*10)
    tb.send_samples(samples)

    # print("Expected results:")
    # print(acquisition(tb.samples_quant, 4.092e6, 10e3, 1000, threshold=0))

    print("Getting results")

    time.sleep(2)
    print(f"Input count: {tb.csr_stream.read(0x04)}")
    print(f"Result count: {tb.csr_stream.read(0x08)}")

    for _ in range(32):
        print(tb.get_results())
