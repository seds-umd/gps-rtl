"""Timing sign-off parsing in the Arty S7 build script."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[2] / "hw" / "integration" / "arty_s7" / "arty_s7.py"
HAVE_LITEX = importlib.util.find_spec("litex") is not None and importlib.util.find_spec("litex_boards") is not None

SUMMARY_GOOD = "      1.218        0.000                      0                11039        0.080        0.000                      0                10326        3.000        0.000                       0                  4353"

REPORT = """
1. checking no_clock (0)
2. checking constant_clock (0)
3. checking pulse_width_clock (0)
4. checking unconstrained_internal_endpoints (0)
5. checking no_input_delay (2)
6. checking no_output_delay (5)
7. checking multiple_clock (0)
8. checking generated_clocks (0)
9. checking loops (0)
10. checking partial_input_delay (0)
11. checking partial_output_delay (0)
12. checking latch_loops (0)

| Design Timing Summary

    WNS(ns)      TNS(ns)  TNS Failing Endpoints  TNS Total Endpoints      WHS(ns)      THS(ns)  THS Failing Endpoints  THS Total Endpoints     WPWS(ns)     TPWS(ns)  TPWS Failing Endpoints  TPWS Total Endpoints
    -------      -------  ---------------------  -------------------      -------      -------  ---------------------  -------------------     --------     --------  ----------------------  --------------------
""" + SUMMARY_GOOD + """

| Inter Clock Table

From Clock    To Clock          WNS(ns)      TNS(ns)  TNS Failing Endpoints  TNS Total Endpoints
----------    --------          -------      -------  ---------------------  -------------------
main_clkout1  main_clkout0        3.404        0.000                      0                  708
main_clkout0  main_clkout1        5.707        0.000                      0                   21

| Other Path Groups Table
"""


@unittest.skipUnless(HAVE_LITEX, "LiteX is not installed (see requirements/litex.txt)")
class TimingGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("arty_s7", SCRIPT)
        cls.script = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.script)

    def test_clean_report_passes(self):
        result = self.script.read_timing(REPORT)
        self.assertTrue(result["timing_met"])
        self.assertEqual((result["setup_wns_ns"], result["hold_whs_ns"], result["pulse_width_wpws_ns"]),
                         (1.218, 0.08, 3.0))
        self.assertEqual(len(result["clock_crossings"]), 2)

    def test_each_fault_fails_closed(self):
        faults = {
            "negative setup slack": REPORT.replace("      1.218        0.000                      0", "     -0.218       -0.400                      3"),
            "negative hold slack": REPORT.replace("        0.080        0.000                      0", "       -0.010       -0.010                      1"),
            "negative pulse width": REPORT.replace("        3.000        0.000                       0", "       -0.100       -0.100                       1"),
            "unclocked register": REPORT.replace("checking no_clock (0)", "checking no_clock (1)"),
            "unconstrained endpoint": REPORT.replace("unconstrained_internal_endpoints (0)", "unconstrained_internal_endpoints (4)"),
            "combinational loop": REPORT.replace("checking loops (0)", "checking loops (1)"),
            "crossing constrained one way only": REPORT.replace("main_clkout0  main_clkout1        5.707        0.000                      0                   21\n", ""),
            "crossing violated": REPORT.replace("        3.404        0.000                      0", "       -0.404       -0.404                      2"),
            "no crossings at all": REPORT.replace("main_clkout", "# main_clkout"),
            "check section missing": REPORT.replace("checking latch_loops (0)", ""),
            "empty report": "",
            "garbage": "not a timing report",
        }
        for name, text in faults.items():
            self.assertNotEqual(text, REPORT, name)
            self.assertFalse(self.script.read_timing(text)["timing_met"], name)

    def test_asynchronous_ports_do_not_fail_the_gate(self):
        # The UART, reset button and LEDs have no I/O delay constraints by design.
        result = self.script.read_timing(REPORT)
        self.assertEqual((result["timing_checks"]["no_input_delay"], result["timing_checks"]["no_output_delay"]), (2, 5))
        self.assertTrue(result["timing_met"])


if __name__ == "__main__":
    unittest.main()
