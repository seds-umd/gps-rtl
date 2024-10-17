import cocotb
from cocotb.triggers import ClockCycles

import fpga_utils.spinal_stream as stream
from fpga_utils import TbTemplate, test_runner

import numpy as np
import matplotlib.pyplot as plt


def from_sfix(val: int, peak: int, width: int):
    # 1 bit less because of sign
    shift = width - peak - 1

    if val >= 2 ** (width - 1):
        val = val - 2**width

    res = val / 2 ** (shift)

    return res


def to_sfix(val: float, peak: int, width: int):
    assert val <= 2**peak * (1.0 - (1.0 / 2 ** (width - 1)))
    assert val >= -(2**peak)

    shift = width - peak - 1

    if shift >= 0:
        val = val * (1 << shift)
    else:
        val = val / (1 << -shift)

    if val < 0:
        val = val + 2**width

    return int(val)


class PLL:
    def __init__(self, bw: float, zeta: float, gain: float, ts: float):
        """Phase locked loop

        Args:
            bw (float): Noise bandwidth
            zeta (float): Damping ratio
            gain (float): Loop gain
            ts (float): Sampling time
        """

        self.set_params(bw, zeta, gain, ts)
        self.reset()

    def set_params(self, bw: float, zeta: float, gain: float, ts: float):
        w_n = 8 * zeta * bw / (4 * zeta**2 + 1)
        tau1 = gain / (w_n * w_n)
        tau2 = 2 * zeta / w_n

        self.c1 = tau2 / tau1  # derivative term
        self.c2 = ts / tau1  # proportional term

    def update(self, err):
        nco = self.c1 * (err - self.last_err) + err * self.c2

        self.last_err = err

        return nco

    def reset(self):
        self.last_err = 0
        self.last_nco = 0


class TestModel:
    def __init__(self, f: float, df: float = 0, ts=1e-3):
        self.ts = 1e-3
        self.ref_freq = lambda t: np.exp(2j * np.pi * (f + df * t) * t)

        self.reset(0)

    def reset(self, f_est):
        self.f_est = f_est
        self.t = 0
        self.phase = 0
        self.freq = f_est

        self.arr_t = []
        self.arr_y = []
        self.arr_freq = []
        self.arr_err = []
        self.arr_nco = []

    def get_err(self) -> float:
        y = self.ref_freq(self.t)
        baseband = y * np.exp(-1j * self.phase)
        self.phase += 2 * np.pi * self.freq * self.ts

        # Phase discriminator - scaled to +-1
        err = np.arctan(baseband.imag / baseband.real) * 2 / (np.pi)

        self.arr_t.append(self.t)
        self.arr_y.append(y)
        self.arr_err.append(err)

        return err

    def set_nco(self, nco: float):
        self.freq = self.freq + nco
        self.t += self.ts

        self.arr_freq.append(self.freq)
        self.arr_nco.append(nco)


class Tb(TbTemplate):
    def __init__(self, dut):
        super().__init__(dut)

        self.err_bus = stream.SpinalStreamSource.from_prefix(self.dut, "io_err")
        self.nco_bus = stream.SpinalStreamSink.from_prefix(self.dut, "io_nco")

        self.err_peak = 0
        self.nco_peak = 3
        self.width = 8

    def put_err(self, err: float):
        val = to_sfix(err, self.err_peak, self.width)
        self.err_bus.write_nowait([val])

    async def get_nco(self) -> float:
        val = await self.nco_bus.read()
        return from_sfix(val, self.nco_peak, self.width)

    async def run(self):
        ts = 1e-3
        pll = PLL(10, 0.707, 0.25, ts)

        N = 1000

        f0 = 100
        df = 30
        f_est = 150

        model = TestModel(f0, df, ts=ts)
        model.reset(f_est)

        model_ref = TestModel(f0, df, ts=ts)
        model_ref.reset(f_est)

        for i in range(N):
            err = model.get_err()
            self.put_err(err)
            nco = await self.get_nco()
            model.set_nco(nco)

            err = model_ref.get_err()
            nco = pll.update(err)
            model_ref.set_nco(nco)

        t = np.array(model.arr_t)

        plt.subplot(2, 1, 1)
        plt.plot(t, model.arr_freq)
        plt.plot(t, model_ref.arr_freq)
        plt.subplot(2, 1, 2)
        plt.plot(t, model.arr_err)
        plt.plot(t, model_ref.arr_err)
        plt.tight_layout()
        plt.savefig("output.png")


@cocotb.test
async def test_pll(dut):
    tb = Tb(dut)
    await tb.reset()

    await tb.run()
    await ClockCycles(dut.clk, 100)

    assert dut.io_locked.value.integer == 1


if __name__ == "__main__":
    test_runner.run_wrapper(
        top_level="Pll",
        package="gps",
        proj_dir="../../..",
        source_dir="hw/spinal/gps",
        gen_dir="hw/gen",
    )
