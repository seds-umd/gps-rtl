import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

script = Path(__file__).resolve().parents[1] / 'check_results.py'
spec = importlib.util.spec_from_file_location('check_results', script)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ResultTests(unittest.TestCase):
    def check(self, xml):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'results.xml'
            path.write_text(xml)
            return module.check_results(path)

    def test_passing_result(self):
        self.assertEqual(self.check('<testsuites><testsuite><testcase name="ok"/></testsuite></testsuites>'), 1)

    def test_rejects_failed_empty_skipped_and_malformed_results(self):
        for body in ['<testcase><failure message="wrong output"/></testcase>',
                     '<testcase><error/></testcase>', '<testcase><skipped/></testcase>', '']:
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.check(f'<testsuite>{body}</testsuite>')
        with self.assertRaises(ET.ParseError):
            self.check('truncated XML')

    def test_missing_results(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(OSError):
            module.check_results(Path(directory) / 'missing.xml')


if __name__ == '__main__':
    unittest.main()
