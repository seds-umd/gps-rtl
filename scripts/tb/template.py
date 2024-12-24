import stream

import logging
import numpy as np
import time
import threading
import inspect
import os
from datetime import datetime


FS = 4.092e6


# Convert complex samples into IQ format for
def process_samples(samples):
    # Normalize - scaling optimized for SNR
    samples /= np.max(np.abs(samples))
    samples *= 127

    assert len(samples) % 2 == 0, "Must have an even number of samples"

    # Convert to 4 bit format
    samples_re = samples.real.astype(np.int8).astype(np.uint8) >> 6
    samples_im = samples.imag.astype(np.int8).astype(np.uint8) >> 6
    bits = (
        samples_re[1::2]
        | (samples_im[1::2] << 2)
        | (samples_re[::2] << 4)
        | (samples_im[::2] << 6)
    )

    # Get quantized samples
    samples_re = (samples_re << 6).astype(np.int8) | 0b100000
    samples_im = (samples_im << 6).astype(np.int8) | 0b100000

    samples_quant = samples_re + samples_im * 1j
    samples_quant /= 128

    return bits, samples_quant


class TemplateTb:
    def __init__(self, dest, port):
        logging.basicConfig(
            filename=f"logs/{os.path.basename(inspect.stack()[-1][1]).split('.')[0]}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
            format="%(asctime)s:%(levelname)s:%(message)s",
            level=logging.INFO,
        )
        self.log = logging.getLogger(__name__)
        self.log.info("Initializing")

        self.iq_stream = stream.StreamInterface(dest, port)
        self.csr_stream = stream.AxilInterface(dest, 1000)
        self.reset()

        build_time = datetime.fromtimestamp(self.get_build_time())
        self.log.info(f"Build Time: {build_time.strftime('%Y-%m-%d %I:%M:%S %p')}")
        print(f"Build Time: {build_time.strftime('%Y-%m-%d %I:%M:%S %p')}")

        # seed = np.random.randint(2**32)
        # self.rng = np.random.default_rng(seed)
        # logging.info(f"Initializing RNG with seed {seed}")

    # def __del__(self):
    #     self.reset()

    def reset(self):
        self.csr_stream.write(0x00, 0)
        time.sleep(0.05)

    # Get unix timestamp
    def get_build_time(self) -> int:
        return self.csr_stream.read(0xFFC)

    # def randn(self, size):
    #     return self.rng.normal(1, 1, size)

    # Test function, returns score
    def test(self) -> float:
        raise NotImplementedError

    def run(self):
        count = 0
        total_score = 0
        last_print = time.time()

        # Gracefully exit when done
        try:
            while True:
                total_score += self.test()
                count += 1

                if time.time() - last_print > 60:
                    last_print = time.time()
                    logging.info(
                        f"Average score: {total_score/count:0.4f}, runs: {count}"
                    )
        except KeyboardInterrupt:
            pass


class IqTestbench(TemplateTb):
    def __init__(self, ip, port=1010):
        super().__init__(ip, port)
        self.thread = None

    def get_availability(self) -> int:
        return self.csr_stream.read(0x10)

    def send_file(self, file, dtype, count: int = -0.5, threaded=False):
        data = np.fromfile(file, dtype=dtype, count=int(count * 2))
        power = -128.5

        samples = data[::2].astype(np.complex64) + 1j * data[1::2].astype(np.complex64)

        # Code for adding noise, disabled for now
        # # Create noise at unity power
        # noise = np.random.uniform(-1, 1, len(samples)) + 1j * np.random.uniform(-1, 1, len(samples))
        # # Power is 2/3 = var(Re) + var(Im)
        # noise /= np.sqrt(2/3)

        # # Set noise level to correct ratio
        # noise_power_dbm = -174 + 10 * np.log10(4.092e6)
        # snr_db = power - noise_power_dbm
        # snr_ratio = 10 ** (snr_db / 10)
        # noise /= np.sqrt(snr_ratio)

        # # Add noise to samples
        # samples = samples + noise

        # # Normalize back to unity power
        # samples = samples / np.sqrt(np.var(samples))

        self.send_samples(samples, threaded)

    def send_samples(self, samples, threaded=False):
        if threaded:
            self.wait_for_thread()

            self.thread = threading.Thread(
                target=self._run, args=(samples,), daemon=True
            )
            self.thread.start()
        else:
            self._run(samples)

    def wait_for_thread(self):
        if self.thread is not None:
            self.thread.join()

    def _run(self, samples):
        bits_bytes, self.samples_quant = process_samples(samples)

        i = 0
        start = time.time()
        chunk_size = self.get_availability()

        while i < len(bits_bytes):
            self.iq_stream.send(bits_bytes[i : i + chunk_size])
            i += chunk_size
            chunk_size = self.get_availability()

        end = time.time()
        # logging.info(f"Speed: {8*(len(bits_bytes)/(end-start))/1e6:.1f} Mb/s")
