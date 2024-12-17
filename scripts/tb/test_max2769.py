import time

import matplotlib.pyplot as plt
import numpy as np
import template
from gps import gps


def normalize_iq(sample: int):
    re = sample & 0b11
    im = (sample >> 2) & 0b11

    # 0x1F bias is optimized to reduce DC offset
    re = (re << 6) | 0x1F
    im = (im << 6) | 0x1F

    re = np.array(re).astype(np.int8)
    im = np.array(im).astype(np.int8)

    c = re - im * 1j
    c /= 128

    return c


class Max2769Testbench(template.TemplateTb):
    def __init__(self, dest):
        super().__init__(dest, 1030)

        self.iq_stream.use_last = False

    def write_reg(self, addr, val):
        assert addr == (addr & 0xF)
        assert val == (val & 0xFFFFFFF)

        data = addr | (val << 4)

        self.csr_stream.write(0x300, data)

    def write_conf1_reg(
        self,
        lnamode: int,
        anten: int,
        fcen: int,
        fbw: int,
        f3or5: int,
        fcenx: int,
        fgain: int,
        chipen: int = 1,
        idle: int = 0,
        mixpole: int = 0,
        mixen: int = 1,
    ):
        reserved = 0x229 << 16

        val = (
            ((chipen & 0x1) << 27)
            | ((idle & 0x1) << 26)
            | ((mixpole & 0x1) << 15)
            | ((lnamode & 0x3) << 13)
            | ((mixen & 0x1) << 12)
            | ((anten & 0x1) << 11)
            | ((fcen & 0x3F) << 5)
            | ((fbw & 0x3) << 3)
            | ((f3or5 & 0x1) << 2)
            | ((fcenx & 0x1) << 1)
            | (fgain & 0x1)
            | reserved
        )

        # print(f"Write conf 1: {hex(val)}")
        self.write_reg(0x00, val)

    def write_conf2_reg(
        self,
        iqen: int = 1,
        gainref: int = 170,
        agcmode: int = 0,
        format: int = 2,
        bits: int = 2,
        drvcfg: int = 0,
    ):
        reserved = 0x1 << 3

        val = (
            ((iqen & 0x1) << 27)
            | ((gainref & 0x1FF) << 15)
            | ((agcmode & 0x3) << 11)
            | ((format & 0x3) << 9)
            | ((bits & 0x7) << 6)
            | ((drvcfg & 0x3) << 4)
            | reserved
        )

        # print(f"Write conf 2: {hex(val)}")
        self.write_reg(0x01, val)

    def write_conf3_reg(
        self,
        gainin: int,
        hiloaden: int,
        fhipen: int,
        pgaien: int,
        pgaqen: int,
        strmen: int,
        strmstart: int,
        strmstop: int,
        strmbits: int,
        stampen: int,
        timesyncen: int,
        datasyncen: int,
        strmrst: int,
    ):
        reserved = (0x1 << 21) | (0xF << 16) | (0x1 << 14) | (0x7 << 6)

        val = (
            ((gainin & 0x3F) << 22)
            | ((hiloaden & 0x1) << 20)
            | ((fhipen & 0x1) << 16)
            | ((pgaien & 0x1) << 13)
            | ((pgaqen & 0x1) << 12)
            | ((strmen & 0x1) << 11)
            | ((strmstart & 0x1) << 10)
            | ((strmstop & 0x1) << 9)
            | ((strmbits & 0x3) << 4)
            | ((stampen & 0x1) << 3)
            | ((timesyncen & 0x1) << 2)
            | ((datasyncen & 0x1) << 1)
            | ((strmrst & 0x1) << 0)
            | reserved
        )

        # print(f"Write conf 3: {hex(val)}")
        self.write_reg(0x02, val)

    def write_clock_reg(self, l: int, m: int, fclk, adcclk, serclk, mode):
        val = (
            ((l & 0xFFF) << 16)
            | ((m & 0xFFF) << 4)
            | ((fclk & 0x1) << 3)
            | ((adcclk & 0x1) << 2)
            | ((serclk & 0x1) << 1)
            | (mode & 0x1)
        )
        # print(f"Write clock reg: {hex(val)}")
        self.write_reg(0x07, val)

    def set_enable(self, en: bool = True):
        self.iq_stream.send(bytes([0x0 if en else 0x1]))

    def get_samples(self, count):
        samples = []

        self.iq_stream.rx_frames = list()
        self.set_enable(True)

        last = len(self.iq_stream.rx_frames)
        while len(self.iq_stream.rx_frames) * 1000 < count:
            time.sleep(0.01)
            curr = len(self.iq_stream.rx_frames)
            if last == curr:
                raise TimeoutError()
            last = curr

        self.set_enable(False)

        while len(samples) < count:
            incoming = self.iq_stream.recv()

            # Decode bytes
            for b in incoming:
                samples.append(b & 0xF)
                samples.append(b >> 4)

        samples = normalize_iq(np.array(samples))

        return samples[:count]

    # Returns frequency of clk, sync, data
    def measure_freqs(self, count=10):
        avgs = np.zeros(3)

        for _ in range(count):
            self.csr_stream.write(0x310, 0)
            time.sleep(0.05)

            avgs[0] += 1e2 * self.csr_stream.read(0x310)
            avgs[1] += 1e2 * self.csr_stream.read(0x314)
            avgs[2] += 1e2 * self.csr_stream.read(0x318)

        return tuple(avgs / count)


def setup_regs_default(tb: Max2769Testbench):
    tb.write_conf1_reg(
        lnamode=2,
        anten=0,
        fcen=0,
        fbw=0,
        f3or5=0,
        fcenx=0,
        fgain=1,
    )
    tb.write_conf2_reg()
    tb.write_conf3_reg(
        gainin=58,
        hiloaden=0,
        fhipen=1,
        pgaien=1,
        pgaqen=1,
        strmen=0,
        strmstart=0,
        strmstop=1,
        strmbits=3,
        stampen=0,
        timesyncen=0,
        datasyncen=1,
        strmrst=0,
    )
    tb.write_reg(0x03, 0x8EC0008)  # REFOUT off for now
    tb.write_reg(0x04, 0x0C08080)
    tb.write_reg(0x05, 0x0000070)
    tb.write_reg(0x06, 0x8000000)
    tb.write_clock_reg(l=1024, m=1024, fclk=1, adcclk=0, serclk=0, mode=1)
    tb.write_conf3_reg(
        gainin=58,
        hiloaden=0,
        fhipen=1,
        pgaien=1,
        pgaqen=1,
        strmen=1,
        strmstart=1,
        strmstop=0,
        strmbits=3,
        stampen=0,
        timesyncen=0,
        datasyncen=1,
        strmrst=0,
    )


def setup_regs_if(tb: Max2769Testbench):
    # 32*1.023 MHz CLK_SER
    # 8*1.023 MHz CLK_ADC
    # 2*1.023 MHz F_IF
    tb.write_conf1_reg(
        chipen=1,
        lnamode=2,
        anten=0,
        fcen=11,
        fbw=0,
        f3or5=0,
        fcenx=1,
        fgain=1,
    )
    tb.write_conf2_reg()
    tb.write_conf3_reg(
        gainin=58,
        hiloaden=0,
        fhipen=1,
        pgaien=1,
        pgaqen=1,
        strmen=0,
        strmstart=0,
        strmstop=1,
        strmbits=3,
        stampen=0,
        timesyncen=0,
        datasyncen=1,
        strmrst=0,
    )
    tb.write_reg(0x03, 0x98C0008)
    tb.write_reg(0x04, 0x0C04080)
    tb.write_reg(0x05, 0x0000070)
    tb.write_reg(0x06, 0x8000000)
    tb.write_clock_reg(l=1024, m=1024, fclk=1, adcclk=0, serclk=0, mode=1)
    tb.write_conf3_reg(
        gainin=58,
        hiloaden=0,
        fhipen=1,
        pgaien=1,
        pgaqen=1,
        strmen=1,
        strmstart=1,
        strmstop=0,
        strmbits=3,
        stampen=0,
        timesyncen=0,
        datasyncen=1,
        strmrst=0,
    )


def waterfall(tb: Max2769Testbench, fs: float, n: int, lines: int):
    samples = tb.get_samples(n * lines)
    Xs = np.zeros((lines, n), dtype=np.complex64)

    for i in range(lines):
        x = samples[i * n : (i + 1) * n]
        X = np.fft.fftshift(np.fft.fft(x)) / len(x)
        Xs[i] = X

    plt.figure(figsize=(8, 8), dpi=300)
    plt.imshow(
        np.abs(Xs),
        aspect="auto",
        extent=(-fs / 2e6, fs / 2e6, n * lines / fs, 0),
    )
    plt.xlabel("Frequency Offset (MHz)")
    plt.ylabel("Time (s)")
    plt.tight_layout()
    plt.savefig("waterfall.png")

    return samples, Xs


def main():
    # fs = 4.092e6*2
    fs = 4.092e6
    N = 1023
    lines = 1000

    tb = Max2769Testbench("10.0.0.2")

    # setup_regs_if(tb)
    # setup_regs_default(tb)
    # return

    # while True:
    #     setup_regs_default(tb)
    #     # setup_regs_if(tb)
    #     time.sleep(0.05)
    #     f_clk_ser, _, f_sync = tb.measure_freqs()
    #     # print(f_clk_ser, f_sync)

    #     if abs(f_clk_ser - 16 * 1.023e6) < 1e4 and abs(f_sync - 1.023e6 / 4) < 1e4:
    #         break

    #     print(".", end="", flush=True)

    print("Configured")

    samples, Xs = waterfall(tb, fs, N, lines)

    X_avg = 10 * np.log10(np.mean(np.abs(Xs), axis=0))
    f = np.linspace(-fs / 2, fs / 2, len(X_avg))

    plt.figure(figsize=(8, 6), dpi=300)
    plt.plot(f / 1e6, X_avg)
    plt.grid()
    plt.tight_layout()
    plt.savefig("out2.png")

    # Save 60s of data (approximately 3.7GB)
    # np.save("max2769_-50dB_many.npy", tb.get_samples(int(60*fs)))

    results = []

    for _ in range(50):
        samples = tb.get_samples(2**15)
        res = gps.acquisition(samples, fs, 30e3, 500, threshold=0, sv=10)
        # res = gps.acquisition(samples, fs, 30e3, 500, fs/4, threshold=0, sv=10)

        # if len(res) > 0:
        #     print(res)
        results.extend(res)

    snr_avg = np.mean([x[3] for x in results])
    snr_max = np.max([x[3] for x in results])
    print(f"Average SNR: {snr_avg:.2f} dB, max: {snr_max:.2f} dB")


if __name__ == "__main__":
    main()
