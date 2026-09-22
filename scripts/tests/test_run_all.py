"""Exercise the shell entry point without an HDL toolchain."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class RegressionEntryPointTest(unittest.TestCase):
    def test_real_exit_status_and_results(self):
        cases = [
            ("<testsuite><testcase/></testsuite>", 0, True),
            ("<testsuite><testcase><failure/></testcase></testsuite>", 0, False),
            ("<testsuite><testcase><error/></testcase></testsuite>", 0, False),
            ("<testsuite/>", 0, False),
            ("<testsuite><testcase><skipped/></testcase></testsuite>", 0, False),
            (None, 0, False),
            ("<testsuite><testcase/></testsuite>", 1, False),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "hw/tb/Example").mkdir(parents=True)
            (root / "scripts").mkdir()
            shutil.copy(ROOT / "hw/tb/run_all.sh", root / "hw/tb/run_all.sh")
            shutil.copy(ROOT / "scripts/check_results.py", root / "scripts/check_results.py")
            bench = root / "hw/tb/Example"
            for xml, code, passing in cases:
                with self.subTest(xml=xml, code=code):
                    # Seed stale passing results; the runner must remove them.
                    (bench / "sim_build").mkdir(exist_ok=True)
                    (bench / "sim_build/results.xml").write_text("<testsuite><testcase/></testsuite>")
                    script = "from pathlib import Path\n"
                    if xml is not None:
                        script += f"Path('sim_build/results.xml').write_text({xml!r})\n"
                    script += f"raise SystemExit({code})\n"
                    (bench / "test_example.py").write_text(script)
                    result = subprocess.run(["bash", "hw/tb/run_all.sh"], cwd=root,
                                            env=dict(os.environ, SKIP_TESTS=""), capture_output=True)
                    self.assertEqual(result.returncode == 0, passing, result.stdout + result.stderr)
            result = subprocess.run(["bash", "hw/tb/run_all.sh", "Typo"], cwd=root, capture_output=True)
            self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
