import template
from gps import gps_sim, gps

import matplotlib.pyplot as plt
import numpy as np
import time


def extract_signed(data: int, width: int):
    val = data & ((1 << width) - 1)
    data >>= width

    if val > 2 ** (width - 1):
        val -= 2 ** width

    return data, val


def extract_complex(data: int, width: int):
    data, re = extract_signed(data, width)
    data, im = extract_signed(data, width)

    return data, re + 1j * im


class TrackingTestbench(template.IqTestbench):
    def __init__(self, ip: str):
        super().__init__(ip, 1040)

    def get_availability(self):
        return int(1e6)

    def tracking_config(self, sv, freq_offset, phase_offset):
        val = sv & 0x3F
        val |= (freq_offset & 0xFFF) << 6
        val |= (phase_offset & 0xFFF) << 18

        self.csr_stream.write(0x210, val)
        self.csr_stream.write(0x214, 0) # need to write to trigger valid

    def get_debug_data(self):
        data = self.iq_stream.recv()
        data = int.from_bytes(data, "little")

        data, early = extract_complex(data, 14)
        data, prompt = extract_complex(data, 14)
        data, late = extract_complex(data, 14)
        data, carr_err = extract_signed(data, 8)
        data, carr_nco = extract_signed(data, 8)

        carr_err /= 2**7
        carr_nco /= 2**3

        return early, prompt, late, carr_err, carr_nco


if __name__ == "__main__":
    tb = TrackingTestbench("10.0.0.2")

    # Unit of frequency offset
    freq_step = 4.092e6 / 4096 / 8

    sv = 1
    freq_offset = 10
    code_phase = 0

    np.random.seed(2598793427)
    samples = gps_sim.generate_gps(
        4.092e6,
        4092*50,
        sv,
        freq_offset * freq_step,
        sample_phase=code_phase,
        # signal_power=-128.5,
        signal_power=-120,
    )

    print("Input Count: ", tb.csr_stream.read(0x200))
    print("Output Count: ", tb.csr_stream.read(0x204))
    print("Input Hash: ", hex(tb.csr_stream.read(0x20C)))
    print("Output Hash: ", hex(tb.csr_stream.read(0x208)))
    print(np.sum(samples))
    tb.tracking_config(sv, freq_offset, code_phase)
    # tb.send_samples(samples)
    time.sleep(0.1)

    for i in range(0, 10, 2):
        tb.send_samples(samples[i:i+2])

        t = tb.csr_stream.read(0x208)
        print(i, t, tb.csr_stream.read(0x200))

        if t != 0:
            print(i, t)
            break

    prompts = []
    carr_errs = []
    carr_ncos = []

    try:
        while True:
            _, prompt, _, carr_err, carr_nco = tb.get_debug_data()

            prompts.append(prompt)
            carr_errs.append(carr_err)
            carr_ncos.append(carr_nco)
    except IndexError:
        pass

    time.sleep(0.5)

    print("Received packets", len(prompts))
    print("Input Count: ", tb.csr_stream.read(0x200))
    print("Output Count: ", tb.csr_stream.read(0x204))
    print("Input Hash: ", hex(tb.csr_stream.read(0x20C)))
    # print("Output Hash: ", hex(tb.csr_stream.read(0x208)))
    print("Output Hash: ", tb.csr_stream.read(0x208))

    prompts = np.array(prompts)
    frequencies = freq_offset * freq_step + np.cumsum(carr_ncos)

    print(np.sum(prompts))

    plt.figure(figsize=(8, 8), dpi=300)

    plt.subplot(2, 2, 1)
    plt.title("Carrier Discriminator")
    plt.plot(carr_errs)

    plt.subplot(2, 2, 2)
    plt.title("Carrier NCO")
    plt.plot(carr_ncos)

    plt.subplot(2, 2, 3)
    plt.title("Frequency Estimate")
    plt.plot(frequencies)

    plt.subplot(2, 2, 4)
    plt.plot(prompts.real)
    plt.plot(prompts.imag)

    plt.tight_layout()
    plt.savefig("tracking.png")
