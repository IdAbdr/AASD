"""Run the stdlib unittest suite and emit a real JUnit XML report for Jenkins."""
import argparse
import sys
import time
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []

    def startTest(self, test):
        self.started = time.perf_counter()
        super().startTest(test)

    def record(self, test, kind=None, message=None):
        self.records.append((test.id(), time.perf_counter() - self.started, kind, message))

    def addSuccess(self, test):
        super().addSuccess(test)
        self.record(test)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.record(test, "failure", self._exc_info_to_string(err, test))

    def addError(self, test, err):
        super().addError(test, err)
        self.record(test, "error", self._exc_info_to_string(err, test))

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.record(test, "skipped", reason)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", default="reports/junit.xml")
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT))
    if suite.countTestCases() == 0:
        parser.error("No tests discovered; refusing to report a successful build.")
    result = unittest.TextTestRunner(verbosity=2, resultclass=RecordedResult).run(suite)
    tree = ET.Element("testsuite", name="SkinResearch", tests=str(result.testsRun),
                      failures=str(len(result.failures)), errors=str(len(result.errors)),
                      skipped=str(len(result.skipped)))
    for identifier, duration, kind, message in result.records:
        classname, name = identifier.rsplit(".", 1)
        case = ET.SubElement(tree, "testcase", classname=classname, name=name, time=f"{duration:.6f}")
        if kind:
            ET.SubElement(case, kind).text = message
    target = Path(args.junit)
    target.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(tree).write(target, encoding="utf-8", xml_declaration=True)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
