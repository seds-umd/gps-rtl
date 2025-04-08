import matplotlib.pyplot as plt
import numpy as np
import pickle

import common
from gps import prn_gen


def quantize(val: float, peak: int, width: int):
    val = int(np.round(val * 2 ** (width - peak - 1))) / 2 ** (width - peak - 1)
    return val


# Modified PLL to match sim behavior
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
        # nco = self.last_nco + self.c1 * (err - self.last_err) + err * self.c2
        nco = self.c1 * (err - self.last_err) + err * self.c2

        self.last_err = err
        self.last_nco = nco

        return nco

    def reset(self):
        self.last_err = 0
        self.last_nco = 0


def tracking_model(
    x: np.ndarray,
    f_s: float,
    sv: int,
    freq_est: float,
    code_est: int,
):
    carrier_pll = PLL(10, 0.707, 0.25, 1e-3)
    code_dll = PLL(1, 0.707, 1, 1e-3)

    # Parameters
    ms_count = int(1e3 * len(x) / f_s)
    code_freq_basis = 1.023e6
    early_late_spacing = 0.5

    code_ref = prn_gen.generate(sv)
    code_ref = np.concatenate([[code_ref[-1]], code_ref, [code_ref[0]]])

    # Variables
    carrier_phase = 0
    carrier_freq = freq_est

    code_phase = 0.5
    code_freq = code_freq_basis

    sample_position = int(f_s / 1e3 - code_est)

    results = {
        val: list()
        for val in [
            "early",
            "prompt",
            "late",
            "carr_freq",
            "carr_err",
            "carr_nco",
            "code_freq",
            "code_err",
            "code_nco",
            "carrier_phase",
            "carrier_out",
        ]
    }

    for _ in range(ms_count):
        code_phase_step = code_freq / f_s
        blksize = int(np.ceil((1023 - code_phase) / code_phase_step))

        # Get chunk of data
        raw_signal = x[sample_position : sample_position + blksize]
        sample_position = sample_position + blksize

        # Exit if not enough samples
        if len(raw_signal) < blksize:
            break

        # Generate code replicas
        tcode = code_phase + np.arange(blksize, dtype=float) * code_phase_step
        prompt_code = code_ref[np.ceil(tcode).astype(int)]

        tcode_early = np.ceil(tcode - early_late_spacing).astype(int)
        early_code = code_ref[tcode_early]

        tcode_late = np.ceil(tcode + early_late_spacing).astype(int)
        late_code = code_ref[tcode_late]

        code_phase = tcode[-1] + code_phase_step - 1023

        # Advance phase
        phase_inc = carrier_freq / 2 ** (12 + 3 - 10)
        phase = phase_inc * np.arange(blksize + 1) + 2**10 * carrier_phase / (2 * np.pi)
        phase = np.round(phase)
        phase = phase * 2 * np.pi / 2**10
        carrier_phase = phase[-1] % (2 * np.pi)

        # Shift to DC, remove PRN, and sum
        carrier = np.exp(-1j * phase[:-1])
        baseband = raw_signal * carrier

        results["carrier_phase"].extend(-phase[:-1])
        results["carrier_out"].extend(carrier)

        # Match shift of 6 in Decimate
        prompt = np.sum(baseband * prompt_code) / 2**6
        early = np.sum(baseband * early_code) / 2**6
        late = np.sum(baseband * late_code) / 2**6

        # Normalize to 1
        prompt /= blksize
        early /= blksize
        late /= blksize

        # Update carrier PLL
        carrier_err = np.arctan(prompt.imag / prompt.real) / (2 * np.pi)
        carrier_err = quantize(carrier_err, common.PLL_ERR_PEAK, common.PLL_WIDTH)
        carrier_nco = carrier_pll.update(carrier_err)
        carrier_nco = quantize(carrier_nco, common.PLL_CARR_NCO_PEAK, common.PLL_WIDTH)
        carrier_nco /= 2**4
        old_carr_freq = carrier_freq
        carrier_freq += carrier_nco

        # Update code DLL
        code_err = prompt.real * (early.real - late.real) + prompt.imag * (
            early.imag - late.imag
        )
        code_err = quantize(code_err, common.PLL_ERR_PEAK, common.PLL_WIDTH)
        code_nco = code_dll.update(code_err)
        code_nco = quantize(code_nco, common.PLL_CODE_NCO_PEAK, common.PLL_WIDTH)
        code_freq -= code_nco

        # Save stuff for graphing and debugging
        results["early"].append(early)
        results["prompt"].append(prompt)
        results["late"].append(late)
        results["carr_freq"].append(old_carr_freq)
        results["carr_err"].append(carrier_err)
        results["carr_nco"].append(carrier_nco)
        results["code_freq"].append(code_freq)
        results["code_err"].append(code_err)
        results["code_nco"].append(code_nco)

    results = {key: np.array(val) for key, val in results.items()}

    return results


def graph_samples(
    dec_early: np.ndarray,
    dec_prompt: np.ndarray,
    dec_late: np.ndarray,
    ref_early: np.ndarray,
    ref_prompt: np.ndarray,
    ref_late: np.ndarray,
    cwd: str,
):
    plt.figure(figsize=(12, 8), dpi=300)

    plt.subplot(2, 3, 1)
    plt.title("Actual Early")
    plt.plot(dec_early.real)
    plt.plot(dec_early.imag)

    plt.subplot(2, 3, 2)
    plt.title("Actual Prompt")
    plt.plot(dec_prompt.real)
    plt.plot(dec_prompt.imag)

    plt.subplot(2, 3, 3)
    plt.title("Actual Late")
    plt.plot(dec_late.real)
    plt.plot(dec_late.imag)

    plt.subplot(2, 3, 4)
    plt.title("Reference Early")
    plt.plot(ref_early.real)
    plt.plot(ref_early.imag)

    plt.subplot(2, 3, 5)
    plt.title("Reference Prompt")
    plt.plot(ref_prompt.real)
    plt.plot(ref_prompt.imag)

    plt.subplot(2, 3, 6)
    plt.title("Reference Late")
    plt.plot(ref_late.real)
    plt.plot(ref_late.imag)

    plt.tight_layout()
    plt.savefig(cwd + "samples.png")


def graph_carrier(
    phase: np.ndarray,
    out: np.ndarray,
    ref_phase: np.ndarray,
    ref_out: np.ndarray,
    cwd: str,
):
    plt.figure(figsize=(12, 8), dpi=300)

    phase = phase[: len(ref_phase)]
    out = out[: len(ref_out)]

    phase = np.unwrap(phase)
    ref_phase = np.unwrap(ref_phase)

    plt.subplot(2, 1, 1)
    plt.title("Unwrapped Phase")
    plt.plot(np.unwrap(phase))
    plt.plot(np.unwrap(ref_phase))

    plt.subplot(2, 1, 2)
    plt.title("Actual - Reference Phase")
    plt.plot((phase - ref_phase) * 180 / np.pi)
    plt.ylabel("Deg")

    plt.tight_layout()
    plt.savefig(cwd + "carrier.png")


def graph_carrier_tracking(
    err: np.ndarray,
    nco: np.ndarray,
    freq: np.ndarray,
    err_calc: np.ndarray,
    ref_err: np.ndarray,
    ref_nco: np.ndarray,
    ref_freq: np.ndarray,
    cwd: str,
):
    plt.figure(figsize=(12, 12), dpi=300)

    plt.subplot(3, 2, 1)
    plt.title("Discriminator")
    plt.plot(err)
    plt.plot(ref_err)

    plt.subplot(3, 2, 2)
    plt.title("Discriminator Error")
    plt.plot(err - err_calc, label="Sim-Calc")
    plt.plot(err - ref_err, label="Sim-Ref")
    plt.legend()

    plt.subplot(3, 2, 3)
    plt.title("PLL Output")
    plt.plot(nco)
    plt.plot(ref_nco)

    plt.subplot(3, 2, 5)
    plt.title("Carrier Frequency")
    plt.plot(freq * 125)
    plt.plot(ref_freq * 125)

    plt.tight_layout()
    plt.savefig(cwd + "carrier_tracking.png")


def graph_code_tracking(
    err: np.ndarray,
    nco: np.ndarray,
    freq: np.ndarray,
    ref_err: np.ndarray,
    ref_nco: np.ndarray,
    ref_freq: np.ndarray,
    cwd: str,
):
    plt.figure(figsize=(6, 12), dpi=300)

    plt.subplot(3, 1, 1)
    plt.title("Discriminator")
    plt.plot(err, "-C0")
    plt.plot(ref_err, "-C1")

    plt.subplot(3, 1, 2)
    plt.title("PLL Output")
    plt.plot(nco)
    plt.plot(ref_nco)

    plt.subplot(3, 1, 3)
    plt.title("Code Frequency")
    plt.plot(freq)
    plt.plot(ref_freq - 1.023e6)

    plt.tight_layout()
    plt.savefig(cwd + "code_tracking.png")


def main(in_test: bool = False, filename: str = "data.pickle"):
    if in_test:
        cwd = "./"
    else:
        cwd = "./sim_build/"

    with open(cwd + filename, "rb") as f:
        data: dict = pickle.load(f)

    # Extract data
    sv: int = data["sv"]
    freq_offset: int = data["freq_offset"]
    code_phase: int = data["code_phase"] + 2
    sample_count: int = data["sample_count"]
    dec_early: np.ndarray = data["dec_early"]
    dec_prompt: np.ndarray = data["dec_prompt"]
    dec_late: np.ndarray = data["dec_late"]
    carrier_err: np.ndarray = data["carrier_err"]
    carrier_nco: np.ndarray = data["carrier_nco"]
    code_err: np.ndarray = data["code_err"]
    code_nco: np.ndarray = data["code_nco"]
    samples: np.ndarray = data["samples"]
    samples_biased: np.ndarray = data["samples_biased"]
    carrier_phase: np.ndarray = data["carrier_phase"]
    carrier_out: np.ndarray = data["carrier_out"]
    carr_freq: np.ndarray = data["carr_freq"]
    code_freq_offset: np.ndarray = data["code_freq_offset"]

    dec_early = dec_early / 4092
    dec_prompt = dec_prompt / 4092
    dec_late = dec_late / 4092

    carrier_nco = carrier_nco / 2**5  # left shift of 5
    code_freq_offset = code_freq_offset * 4.092e6 / 2**common.PRN_FREQ_WIDTH

    carrier_err_calc = np.arctan(dec_prompt.imag / dec_prompt.real) / (2 * np.pi)

    # Reference Model
    ref = tracking_model(
        samples_biased, 4.092e6, sv, int(freq_offset / 125), code_phase
    )

    graph_samples(
        dec_early, dec_prompt, dec_late, ref["early"], ref["prompt"], ref["late"], cwd
    )

    graph_carrier(
        carrier_phase, carrier_out, ref["carrier_phase"], ref["carrier_out"], cwd
    )

    graph_carrier_tracking(
        carrier_err,
        carrier_nco,
        carr_freq,
        carrier_err_calc,
        ref["carr_err"],
        ref["carr_nco"],
        ref["carr_freq"],
        cwd,
    )

    graph_code_tracking(
        code_err, code_nco, code_freq_offset, ref["code_err"], ref["code_nco"], ref["code_freq"], cwd
    )


if __name__ == "__main__":
    # main(filename="data_250ms.pickle")
    main()
