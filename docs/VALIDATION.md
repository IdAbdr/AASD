# Evidence and remaining validation

Preparation date: 2026-10-09.

Executed with Python 3.12 and the preparation environment's installed Pillow:
- `python -m unittest discover -s tests -p test_analysis.py -v`: 9 tests passed.
- `python -m compileall -q app.py analysis.py tests`: passed.

Not executed: web integration tests (11), Ruff, remote Actions workflow, multi-version matrix. Flask and Ruff were absent and package downloads were unavailable. Installed Pillow's version is recorded in the accompanying preparation log; it is not evidence that all pinned requirements were installed.

To complete validation, install requirements-dev.txt, run the full test/lint commands from README, push the repository and inspect both Actions jobs. Save the commit hash, successful run URL and screenshots. If any check fails, fix and rerun before submission. A prepared YAML file alone does not demonstrate successful CI.
