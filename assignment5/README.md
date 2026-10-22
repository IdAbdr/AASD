# Assignment 5 DevOps for skin image research

This additive example for https://github.com/IdAbdr/AASD packages deterministic image descriptors.
It does not load trained weights or predict disease. No full HAM10000 download or GPU is needed.

## Browser only cloud lab

Open the repository in GitHub Codespaces with its standard configuration. No Docker Desktop or Jenkins installation on the laptop is required.
Codespaces must have an available allowance or billing access. A custom devcontainer may lack Docker; inspect any failed prerequisite check.
From the repository root in its Bash terminal:

```bash
docker info
docker compose version
bash assignment5/cloud/start.sh
docker compose -f assignment5/cloud/compose.yaml ps
docker compose -f assignment5/cloud/compose.yaml exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

Forward port **8080** in **Ports**, keep it **Private**, and open its HTTPS URL. Complete Jenkins setup and create an administrator.
Under **Manage Jenkins → System → Jenkins Location**, verify **Jenkins URL** matches the forwarded URL including its trailing slash.
The startup Groovy script configures this from Codespaces variables when available; verify the UI result.
Create a **Pipeline** job `SkinResearch-A5` with **Pipeline script from SCM**, **Git**, repository `https://github.com/IdAbdr/AASD.git`,
actual branch `*/main` or `*/master`, and Script Path `assignment5/Jenkinsfile`. Public HTTPS checkout needs no repository credential.
Run **Build Now** once with `DEPLOY_DEMO` enabled. Later pushes are detected by SCM polling every minute; adjacent pushes can be batched.

The pipeline checks out Git, builds a test environment, runs tests, builds the runtime image, checks a candidate and deploys the verified image.
Forward port **8000** privately to open the application. Its `/health` and `/version` identify the source revision.
Forwarded URLs require authorized GitHub access. Cloud terminal localhost is not the laptop localhost.

## Prove the automatic second deployment

Wait for a first successful build and **Demo release 1**. From the repository root:

```bash
python assignment5/cloud/record.py before
python assignment5/cloud/demo_change.py
git add assignment5/service/index.html
git commit -m "Demonstrate automatic cloud deployment"
git push
```

Do not click Build Now for the second build. Wait for SCM polling and successful Deploy demo.
Refresh the app: it must show **Demo release 2** and a new full SHA at `/health`.

```bash
python assignment5/cloud/record.py after
```

Download `assignment5/reports/evidence/before.json`, `after.json` and `proof.json`, plus both builds' Jenkins artifacts.
The recorder checks live revisions, image identities and release labels. It does not establish the Jenkins trigger cause:
capture **Started by an SCM change** from the second build separately. Follow docs/SUBMISSION_CHECKLIST.md and the Russian Word guide.
Evidence recorder snapshots are deliberately not overwritten; preserve the first demonstration results before attempting a fresh run.

## Architecture and limits

The cloud Compose file starts one Jenkins container using the existing Codespaces Docker daemon through its socket.
It does not start another privileged Docker-in-Docker daemon. Jenkins runs as root for socket compatibility in this disposable teaching environment.
Socket access grants broad control over the environment: use only your trusted repository and keep forwarded ports private.
The application container runs as non-root. Jenkins and the test deployment share the same cloud host.
Promotion follows successful tests and candidate smoke checks. A failed deployment attempts to restart the previous image and keeps the build failed.
Verify the restored `/health` before reuse. Runtime images exclude tests and Jenkins configuration.
Pillow is pinned, but base-image tags and Jenkins plugin versions are mutable. Commit and image IDs improve traceability without guaranteeing bit-identical future rebuilds.

## Native checks

From assignment5 with Python 3.12 and Pillow 12.3.0:

```bash
python -m pip install -r requirements.txt
python ci/run_tests.py --junit reports/junit.xml
python -m service.server
```

The unittest suite includes HTTP integration checks. Supported JPEG/PNG uploads remain in memory, with EXIF orientation applied, limited to 8 MiB and 20 megapixels.
Native checks do not replace actual Docker/Jenkins/CD execution evidence.

## Stop and resume

Download evidence first. At https://github.com/codespaces choose your environment → **Stop codespace**.
Closing the tab alone does not guarantee stopping; storage may keep counting while stopped.
To resume, open the same environment and run:

```bash
bash assignment5/cloud/start.sh
docker start skinlab-a5-demo
```

If no deployment exists, first run the pipeline. Check docker ps and privately forward ports 8080/8000 again as needed.
Do not delete the Codespace before saving evidence and completing any planned demonstration.

## Alternative local lab

For computers already running Docker Desktop with Linux containers, the original configuration remains:

```bash
docker compose -f assignment5/jenkins/compose.yaml up -d --build
```

That alternative uses a separate TLS Docker daemon and local ports 8080/8000. Use the cloud configuration for the browser workflow, and do not start both together.
Docker Hub and Kubernetes are optional. Kubernetes is discussed in the theory report.
