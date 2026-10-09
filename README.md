# Skin Image Research Tool

A small scientific image-processing module with a Flask interface, SQLite history and CSV export. It evolves the original skin-disease demo into a reproducible research prototype. **There is no trained disease classifier or medical prediction.** The original random diagnosis and probability have been removed.

## Quick start (Python 3.11 or 3.12)

```bash
python -m venv .venv
```
Windows PowerShell: `.venv\Scripts\Activate.ps1` (or run `.venv\Scripts\python.exe` directly if activation is blocked).
macOS/Linux: `source .venv/bin/activate`.

```bash
python -m pip install -r requirements-dev.txt
python app.py
```
Open http://127.0.0.1:5000. Upload a synthetic JPEG/PNG, open History, then Export CSV. The database is initialized automatically; no manual SQL is needed.

## Scientific method

`analysis.extract_features(source)` accepts a binary file-like object. The image is decoded, checked to be JPEG/PNG and <=20 million pixels, EXIF orientation is applied, then it is converted to 8-bit RGB. All pixels contribute equally. Grayscale uses Pillow's RGB-to-L conversion. Means and grayscale population standard deviation are rounded to four decimal places. Analysis version: `whole-image-v1`.

| Feature | Definition / units |
|---|---|
| width, height | Dimensions after EXIF rotation, pixels |
| mean_red, mean_green, mean_blue | Arithmetic mean of each RGB channel, 0-255 |
| brightness | Mean grayscale intensity, 0-255 |
| contrast | Population standard deviation of grayscale intensity |

A constant black image has brightness=0 and contrast=0. A two-pixel black/white image has brightness=127.5 and contrast=127.5. JPEG compression may change pixel values. Background, illumination, camera and skin tone affect these whole-image summaries; they are not lesion descriptors, malignancy scores or diagnostic confidence.

## Structure

- `app.py`: application factory, upload/results/history/export routes and parameterized SQLite queries.
- `analysis.py`: independently testable numerical module.
- `templates/`, `static/`: interface.
- `tests/`: nine numerical/input tests and eleven web integration tests.
- `.github/workflows/ci.yml`: CI plus delivery of validated source archives.
- `docs/`: method, submission guide, issue drafts and validation status.

## Validation

```bash
python -m unittest discover -s tests -v
ruff check .
python -m compileall -q app.py analysis.py tests
```
The preparation environment passed 9 numerical tests and syntax compilation. It lacked Flask and Ruff and could not download them; the 11 web tests and lint were **not executed locally**. Do not treat the workflow file as proof of a successful remote run. Run the full suite after dependency installation, then confirm both GitHub jobs are green. See `docs/VALIDATION.md`.

## Git and GitHub

Local `.git` history is included in the delivered bundle (three commits). If it is present, do not reinitialize it. Publish the project directory as a public repository. The exact commands and screenshots required for submission are in `docs/SUBMISSION_GUIDE_RU.md`. File templates are supplied for bugs and research improvements; actual GitHub issues still need to be opened.

## CI/CD scope

Pushes, pull requests and manual runs trigger Python 3.11/3.12 jobs. Each installs dependencies, lints, runs all tests, compiles source, archives tracked files and uploads a validated source ZIP. An earlier failure prevents packaging. This is basic continuous integration and artifact delivery, not a production deployment. An artifact still requires Python and dependency installation to run. No server, dataset or clinical service is deployed.

## Technology choices

Python fits an extensible scientific workflow. Flask preserves the existing small web application and supports isolated application factories. Pillow decodes images and computes image statistics without adding a training framework. SQLite avoids a separate database server for a local single-user prototype. Standard-library unittest requires no separate test dependency. Ruff catches common static errors. Git records meaningful revisions; GitHub hosts code, issues and Actions. Git and GitHub are different kinds of tools, not competing version-control systems.

## Limits and data handling

The app binds to loopback and is for local coursework. It has no authentication, multi-user access control, CSRF protection or clinical validation. Files are processed in memory and not stored; SQLite stores only generated IDs, UTC timestamps and numeric descriptors, not original filenames. Use synthetic/non-sensitive public images. Database contents are local and excluded from Git. Delete `instance/research.db` while the app is stopped to clear history. The old uploads and legacy database were deliberately excluded from the new bundle.

Runtime dependencies are pinned directly; transitive dependencies and action tags are not immutable locks. For a long-term release, review current vulnerabilities, create a full dependency lock, and pin actions to commit hashes. An actual classifier would require licensed data, subject-level split controls, evaluation, external validation and explicit model-version tracking.

## License

MIT for the supplied software. This does not grant rights to third-party datasets or images. The license holder must be reviewed by the student before public release.
