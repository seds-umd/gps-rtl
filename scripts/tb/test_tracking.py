import template
from gps import gps_sim, gps

import matplotlib.pyplot as plt
import numpy as np
import time


# Tracking module uses the same IQ interface as acquisition
class TrackingTestbench(template.IqTestbench):
    def reset(self):
        super().reset()

        # Enable tracking IQ input
        self.csr_stream.write(0x214, 1)

    def tracking_config(self, sv, freq_offset, phase_offset):
        val = sv & 0x3F
        val |= (freq_offset & 0xFFF) << 6
        val |= (phase_offset & 0xFFF) << 18

        self.csr_stream.write(0x210, val)

    def _get_complex(self, addr, bits: int = 14, timeout=1):
        start = time.time()

        data = 0
        while not (data & (1 << 31)):
            data = self.csr_stream.read(addr)

            if time.time() - start > timeout:
                raise TimeoutError()

            time.sleep(0.01)

        # print(hex(data))

        re = data & ((1 << bits) - 1)
        im = (data >> bits) & ((1 << bits) - 1)

        # print(hex(re), hex(im))

        if re >= 2 ** (bits - 1):
            re = re - 2**bits

        if im >= 2 ** (bits - 1):
            im = im - 2**bits

        res = re + 1j * im

        return res

    def get_tracking_data(self):
        early = self._get_complex(0x200)
        prompt = self._get_complex(0x204)
        late = self._get_complex(0x208)

        return early, prompt, late

    def send_freq_delta(self, value: float):
        exp = 8
        width = 16

        value = value * 2**(width - exp - 1)
        value = int(value)

        if value < 0:
            value = value + 2**width

        self.csr_stream.write(0x20C, value)


if __name__ == "__main__":
    tb = TrackingTestbench("10.0.0.2")

    # Unit of frequency offset
    freq_step = 4.092e6 / 4096 / 8

    sv = 1
    freq_offset = 10
    code_phase = 0

    samples = gps_sim.generate_gps(
        4.092e6,
        4092*150,
        sv,
        freq_offset * freq_step,
        sample_phase=code_phase,
        signal_power=-128.5,
    )

    options = []
    options.extend(range(0, 200))
    options.extend(range(3900, 4092))

    for code in options:
        if code % 64 == 0:
            print(f"i = {code}")

        tb.reset()
        tb.tracking_config(sv, freq_offset, code)
        tb.send_freq_delta(freq_offset)
        tb.send_samples(samples, True)
        # tb.send_file(
        #     "../../../gps-model/data/test0.ci16", np.int8, count=1e6, threaded=True
        # )

        pll = gps.PLL(10, 0.707, 0.25, 1e-3)

        errors = []
        ncos = []
        prompts = []

        for _ in range(100):
            early, late, prompt = tb.get_tracking_data()
            if prompt.real == 0:
                err = np.pi/2 * np.sign(prompt.imag)
            else:
                err = np.arctan(prompt.imag / prompt.real)

            last = pll.last_nco
            nco = pll.update(err) - last
            tb.send_freq_delta(nco / freq_step)

            errors.append(err)
            ncos.append(nco + last)
            prompts.append(prompt)

        plt.figure(figsize=(8, 6), dpi=300)
        plt.subplot(3, 1, 1)
        plt.plot(np.real(prompts))
        plt.plot(np.imag(prompts))
        plt.subplot(3, 1, 2)
        plt.title("Error")
        plt.plot(errors)
        plt.subplot(3, 1, 3)
        plt.title("NCO Frequency")
        plt.plot(ncos)
        plt.tight_layout()
        plt.savefig(f"output/out{code}.png")
        plt.close()
