# Assignment 5 actual execution evidence

1. The public repository includes assignment5/Dockerfile, assignment5/Jenkinsfile and cloud startup files.
2. First real Jenkins build: every required stage succeeds, including Deploy demo. Record its number, URL and full SHA.
3. Record actual Jenkins test counts and failures. Do not substitute package preparation results.
4. Capture the real Docker build and image tag/ID. Download source-commit.txt, runtime-image.json, junit.xml and deployment-smoke.json into evidence/build1.
5. Privately forward port 8000, process synthetic_rgb.png, capture release 1 and its /health revision.
6. Run python assignment5/cloud/record.py before in the repository root.
7. Run python assignment5/cloud/demo_change.py, commit the HTML and push. Do not manually trigger a second build.
8. Capture the second build SCM trigger cause, successful stages, new SHA and image.
9. Confirm release 2 and its new /health SHA. Run python assignment5/cloud/record.py after and obtain PASS.
10. Download before.json, after.json and proof.json from assignment5/reports/evidence and the second Jenkins build artifacts into evidence/build2.
11. Supply readable screenshots S1_pipeline, S2_tests, S3_image, S4_before, S5_auto and S6_after. Additional PNGs are fine for readable evidence.
12. Fill all practical-report placeholders with observed results and conclusions. Keep practical report 1–2 pages and theory 3–5 pages, 12 pt and 1.5 spacing.
13. Submit both reports, screenshots, evidence and repository/Jenkinsfile links. Capture evidence before stopping Codespaces.

Jenkins artifacts live in its separate container workspace; recorder outputs live in the user's Codespaces working tree. Download both explicitly.
Forwarded URLs are private and temporary, so keep screenshots and outputs. Polling works only while Jenkins/Codespaces run and may batch nearby pushes.
Keep ports private; exclude passwords, tokens and patient data. Docker Hub and Kubernetes are optional.
Prepared files alone do not establish successful CI/CD or guarantee a grade.
