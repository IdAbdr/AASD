"""Make the single visible release change used to demonstrate automatic CD."""
from pathlib import Path
import sys

BEFORE = '<p id="demo-release">Demo release 1</p>'
AFTER = '<p id="demo-release">Demo release 2</p>'


def main():
    target = Path(__file__).resolve().parents[1] / "service" / "index.html"
    text = target.read_text(encoding="utf-8")
    if text.count(BEFORE) != 1 or AFTER in text:
        print("ERROR: Expected exactly one Demo release 1 marker. No file was changed.", file=sys.stderr)
        return 1
    target.write_text(text.replace(BEFORE, AFTER, 1), encoding="utf-8")
    print("Changed assignment5/service/index.html: Demo release 1 -> Demo release 2.")
    print("Commit and push this change, then wait for Jenkins to deploy it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
