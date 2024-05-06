import numpy as np

from cocotbext import axi


# Calculate correlation between two signals, between 1 and -1
def corr(a: np.ndarray, b: np.ndarray):
    assert len(a) == len(b), f"Arrays must be the same length, {len(a)} != {len(b)}"

    a_norm = (a - np.mean(a)) / np.std(a)
    b_norm = (b - np.mean(b)) / np.std(b)

    return np.abs(np.sum(a_norm * b_norm.conjugate())) / len(a)


# Random pause generator for AXI bus
def random_pause():
    while True:
        yield np.random.choice([0, 1])


def stream_axis_bus(dut, prefix: str):
    axi_bus = axi.AxiStreamBus(dut)
    axi_bus._add_signal("tdata", prefix + "payload")
    axi_bus._add_signal("tvalid", prefix + "valid")
    axi_bus._add_signal("tready", prefix + "ready")

    return axi_bus
