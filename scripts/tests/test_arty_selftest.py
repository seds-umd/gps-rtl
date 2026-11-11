"""Protocol and checking code shared by the board self-test host tool and its simulation bench."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import arty_selftest as host  # noqa: E402
import max_emulator as model  # noqa: E402


class ProtocolTests(unittest.TestCase):
    def test_result_line_from_the_board(self):
        # Captured from an Arty S7-25 running the default signal.
        result = host.parse_line(b"R070103E7FF0\r")
        self.assertEqual((result.sv, result.freq_offset, result.phase_offset, result.metric, result.overflow),
                         (7, 16, 999, 255, False))
        self.assertAlmostEqual(result.doppler_hz, 16 * 4.092e6 / 32768)

    def test_negative_frequency_and_overflow_flag(self):
        result = host.parse_line("R20F48FFF0A1")
        self.assertEqual((result.sv, result.freq_offset, result.phase_offset, result.metric, result.overflow),
                         (32, -184, 4095, 10, True))

    def test_replies(self):
        reply = host.parse_line("w0400C0FFEE")
        self.assertEqual((reply.kind, reply.address, reply.value), ("w", 4, 0xC0FFEE))
        self.assertEqual(host.parse_line("i0147505331").value, host.ID_WORD)
        self.assertEqual(host.parse_line("e").kind, "e")
        self.assertIsNone(host.parse_line("  \r\n"))

    def test_garbled_lines_are_rejected(self):
        for line in ("R070103E7FF", "R070103E7FG0", "w04", "x", "q0G00000000", "e1"):
            with self.assertRaises(ValueError, msg=line):
                host.parse_line(line)

    def test_commands(self):
        self.assertEqual(host.write_command(0x11, -1441792), b"W11FFEA0000\n")
        self.assertEqual(host.read_command(2), b"Q02\n")

    def test_scenario_writes_cover_every_channel(self):
        scenario = host.Scenario("s", [model.Channel(7, 1000, host.fine(16), 96)], noise_gain=5, threshold=70, seed=9)
        writes = dict(host.scenario_writes(scenario, 2))
        self.assertEqual(writes[host.REG_QUANT], 5 | (70 << 8))
        self.assertEqual(writes[host.REG_SEED], 9)
        self.assertEqual(writes[host.REG_CHANNEL_BASE], 7 | (1 << 8) | (96 << 16))
        self.assertEqual(writes[host.REG_CHANNEL_BASE + 1], 16 << 17)
        self.assertEqual(writes[host.REG_CHANNEL_BASE + 2], 1000)
        # The unused channel is switched off, not left at its previous setting.
        self.assertEqual(writes[host.REG_CHANNEL_BASE + host.REG_CHANNEL_STRIDE] & 0x100, 0)
        with self.assertRaises(ValueError):
            host.scenario_writes(host.Scenario("s", [model.Channel(33)]), 2)
        with self.assertRaises(ValueError):
            host.scenario_writes(host.Scenario("s", [model.Channel(1, 4092)]), 2)
        with self.assertRaises(ValueError):
            host.scenario_writes(host.Scenario("s", [model.Channel(1), model.Channel(2), model.Channel(3)]), 2)


class CheckTests(unittest.TestCase):
    def setUp(self):
        self.scenario = host.Scenario("s", [model.Channel(2, 37, host.fine(8))])

    def results(self, **changes):
        present = dict(sv=2, freq_offset=8, phase_offset=37, metric=255, overflow=False)
        present.update(changes)
        return [host.Result(1, -777, 3266, 11, False), host.Result(**present)]

    def test_good_results_pass(self):
        self.assertEqual(host.check_results(self.scenario, self.results()), [])
        # Half a chip either way, including across the wrap, is within the estimator's accuracy.
        self.assertEqual(host.check_results(self.scenario, self.results(phase_offset=35)), [])
        wrap = host.Scenario("s", [model.Channel(2, 4091, 0)])
        self.assertEqual(host.check_results(wrap, [host.Result(2, 0, 1, 255, False)]), [])

    def test_each_kind_of_fault_is_reported(self):
        for changes, text in [
            (dict(freq_offset=10), "freq_offset"),
            (dict(phase_offset=40), "phase_offset"),
            (dict(metric=8), "below"),
            (dict(metric=30), "strongest absent"),
            (dict(overflow=True), "overflow"),
        ]:
            problems = host.check_results(self.scenario, self.results(**changes))
            self.assertTrue(any(text in p for p in problems), (changes, problems))
        self.assertTrue(any("no result" in p for p in host.check_results(self.scenario, self.results()[:1])))

    def test_order(self):
        results = [host.Result(sv, 0, 0, 0, False) for sv in (31, 32, 1, 2)]
        self.assertEqual(host.check_order(results, first_sv=31), [])
        self.assertTrue(host.check_order(results))


class ModelTests(unittest.TestCase):
    def test_tables_and_units(self):
        self.assertEqual(len(model.COS_TABLE), 64)
        self.assertEqual(max(model.COS_TABLE), 127)
        self.assertEqual([-v for v in model.COS_TABLE[:32]], model.COS_TABLE[32:])
        self.assertEqual(model.Channel(1, carrier_inc=host.fine(-40)).expected_freq_offset, -40)
        self.assertEqual(model.xorshift32(1), 270369)

    def test_serial_bits_plane_order(self):
        i = list(range(-2, 2)) * 4  # 2-bit codes 10, 11, 00, 01
        q = [1] * 16
        bits = model.serial_bits(i, q)
        self.assertEqual(len(bits), 64)
        self.assertEqual([sync for _, sync in bits], ([1] + [0] * 15) * 4)
        self.assertEqual([b for b, _ in bits[0:4]], [1, 1, 0, 0])  # I MSB
        self.assertEqual([b for b, _ in bits[16:20]], [0, 1, 0, 1])  # I LSB
        self.assertEqual([b for b, _ in bits[32:48]], [0] * 16)  # Q MSB
        self.assertEqual([b for b, _ in bits[48:64]], [1] * 16)  # Q LSB


if __name__ == "__main__":
    unittest.main()
