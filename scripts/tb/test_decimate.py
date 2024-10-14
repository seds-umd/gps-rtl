import stream
import template

import logging
import numpy as np
import time

from fpga_utils.dsp import corr
from fpga_utils.fft_sim import fft_pack_complex, fft_unpack_complex


class DecimateTb(template.TemplateTb):
    def __init__(self):
        super().__init__("10.0.0.2", "10.0.0.1", 1000)

        self.FACTOR = 8
        self.OUT_LEN = int(4096/self.FACTOR)
        self.IQ_SIZE = 2  # bytes per IQ
        self.SAMPLES = self.FACTOR * self.OUT_LEN

    def test(self):
        ref = self.randn(self.SAMPLES) + 1j * self.randn(self.SAMPLES)
        ref /= np.max(np.abs(ref))
        ref_dec = np.sum(ref.reshape(-1, 8), axis=1) / 8

        data = fft_pack_complex(ref)
        data = np.array(data, dtype=">i2")
        data = data.tobytes()
        self.stream.send(data)

        data = self.stream.recv()
        data = np.frombuffer(data, dtype=">i2")
        data = fft_unpack_complex(data)

        score = corr(ref_dec, data)

        return score


if __name__ == "__main__":
    tb = DecimateTb()

    tb.run()
