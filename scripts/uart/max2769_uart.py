import time

import matplotlib.pyplot as plt
import numpy as np
import serial
from gps import gps


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


class Max2769Uart:
    def __init__(self, port, baud=115200):
        self.ser = serial.Serial(port, baud, timeout=0.1)

        self.last_data = bytearray()
        self.buffer = bytearray()
        self.active_request = -1

    def __del__(self):
        try:
            self.ser.close()
        except AttributeError:
            pass

    def request_data(self, size_log=8) -> bool:
        if self.active_request > 0:
            return False

        assert size_log < 0x20, "Size too large"
        self.ser.write(bytes([size_log]))

        return True

    def get_data(self, param=8):
        # Write any data to start transfer
        self.request_data(param)

        buffer = bytearray()
        start = time.time()

        while len(buffer) < 2**param and time.time() - start < 2:
            buffer.extend(self.ser.read_all())

        return buffer

    def get_samples(self, n):
        return decode_samples(self.get_data(n - 1))

    def write_register(self, addr, value):
        assert addr == (addr & 0xF)
        assert value == (value & 0xFFFFFFF)

        combined = (value << 4) | addr

        self.ser.write(bytes([0x20]))
        self.ser.write(combined.to_bytes(4, "big"))


if __name__ == "__main__":
    max = Max2769Uart(
        "/dev/serial/by-id/usb-Digilent_Digilent_USB_Device_210183B167BB-if01-port0",
        baud=3125 * 1000,
    )

    max.write_register(0x00, 0xA2951A1)
    max.write_register(0x01, 0x8550488)
    max.write_register(0x02, 0xA2FEDF2)
    max.write_register(0x04, 0xC08080)
    max.write_register(0x05, 0x70)

    while True:
        samples = max.get_samples(12)
        # results = gps.acquisition(samples, 4.092e6, 100e3, 1000)
        # print(results)
