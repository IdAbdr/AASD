# Create these actual GitHub issues after publication

## Issue 1: Validate the application and complete the coursework evidence
Labels: documentation
- [ ] Install pinned dependencies and run all 20 tests and Ruff.
- [ ] Confirm both GitHub Actions matrix jobs pass.
- [ ] Add the public repository, workflow and successful run links to the report.
- [ ] Capture application/history/CSV and CI screenshots.
Acceptance: attach run URL and commit ID, then close the issue.

## Issue 2: Add dataset-level image quality summaries
Labels: enhancement
Propose batch analysis of an explicitly licensed dataset, CSV aggregation and descriptive plots. Define dataset version, sampling method and normalization before implementation. Acceptance: deterministic batch results, tests against known images and documented dataset permissions.

## Issue 3: Investigate a separately validated classifier
Labels: enhancement
This is future work, not an implemented feature. Select a permitted dataset, perform subject-level splitting, define a baseline and evaluation metrics, track model/data versions and assess bias. Acceptance requires measured held-out results; never reuse the removed random prediction as evidence.
