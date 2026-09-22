"""Fail closed when a simulator did not produce a passing cocotb result."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def check_results(path):
    root = ET.parse(path).getroot()
    cases = list(root.iter('testcase'))
    failed = [c for c in cases if c.find('failure') is not None or c.find('error') is not None]
    executed = [c for c in cases if c.find('skipped') is None]
    if failed or not executed:
        raise ValueError(f'{path}: {len(executed)} executed, {len(failed)} failed')
    return len(executed)


if __name__ == '__main__':
    try:
        count = check_results(Path(sys.argv[1]))
    except (OSError, ET.ParseError, ValueError, IndexError) as error:
        sys.exit(f'Simulation failed: {error}')
    print(f'Simulation passed: {count} test(s)')
