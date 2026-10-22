"""Verify and save real deployment evidence; never manufacture execution results."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import subprocess
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
SHA = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
IMAGE_ID = re.compile(r"sha256:[0-9a-f]{64}\Z")


class VerificationError(Exception):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def command(*args):
    try:
        result = subprocess.run(args, cwd=ROOT, check=True, capture_output=True,
                                text=True, timeout=30)
    except FileNotFoundError as error:
        raise VerificationError(f"Required command not found: {args[0]}") from error
    except subprocess.TimeoutExpired as error:
        raise VerificationError(f"Command timed out: {' '.join(args)}") from error
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip()
        raise VerificationError(f"Command failed: {' '.join(args)}\n{detail}") from error
    return result.stdout.strip()


def inspect(kind, name):
    try:
        records = json.loads(command("docker", kind, "inspect", name))
        require(isinstance(records, list) and len(records) == 1
                and isinstance(records[0], dict), "Docker inspect returned unexpected data.")
        return records[0]
    except json.JSONDecodeError as error:
        raise VerificationError("Docker inspect did not return valid JSON.") from error


def fetch(base, endpoint, as_json=False):
    try:
        with urllib.request.urlopen(base.rstrip("/") + endpoint, timeout=5) as response:
            require(response.status == 200, f"{endpoint} did not return HTTP 200.")
            body = response.read(1024 * 1024 + 1)
        require(len(body) <= 1024 * 1024, f"{endpoint} returned an unexpectedly large body.")
        value = body.decode("utf-8")
        if as_json:
            value = json.loads(value)
            require(isinstance(value, dict), f"{endpoint} must return a JSON object.")
        return value
    except (OSError, ValueError, urllib.error.URLError) as error:
        raise VerificationError(f"Cannot read {endpoint}: {error}") from error


def snapshot(args):
    revision = command("git", "rev-parse", "HEAD")
    require(SHA.fullmatch(revision), "Git HEAD is not a full commit revision.")
    require(Path(command("git", "rev-parse", "--show-toplevel")).resolve() == ROOT.resolve(),
            "Place assignment5 directly inside the root of the Git repository.")
    require(not command("git", "status", "--porcelain", "--untracked-files=all", "--", "assignment5"),
            "Commit or discard changes under assignment5 before recording deployment evidence.")
    container = inspect("container", args.container)
    require(container.get("State", {}).get("Running") is True,
            "The deployed application container is not running.")
    image_id = container.get("Image", "")
    require(IMAGE_ID.fullmatch(image_id), "The container has no valid immutable image ID.")
    image = inspect("image", image_id)
    require(image.get("Id") == image_id, "Container and inspected image IDs differ.")
    require(image.get("Config", {}).get("Labels", {}).get("org.opencontainers.image.revision") == revision,
            "The deployed Docker image was not built from the current Git HEAD.")
    require(f"APP_REVISION={revision}" in (container.get("Config", {}).get("Env") or []),
            "The container APP_REVISION does not match the current Git HEAD.")
    health = fetch(args.base_url, "/health", as_json=True)
    require(health.get("status") == "ok", "Application health is not ok.")
    require(health.get("revision") == revision,
            "The live /health revision does not match Git HEAD. Wait for the correct deployment.")
    version = fetch(args.base_url, "/version", as_json=True)
    require(version.get("revision") == revision, "The live /version revision does not match Git HEAD.")
    release = "Demo release 1" if args.phase == "before" else "Demo release 2"
    marker = f'<p id="demo-release">{release}</p>'
    require((ROOT / "assignment5" / "service" / "index.html").read_text(encoding="utf-8").count(marker) == 1,
            f"The source must contain exactly one {release} marker.")
    require(fetch(args.base_url, "/").count(marker) == 1,
            f"The running home page must display {release}.")
    latest = inspect("container", args.container)
    require(latest.get("Id") == container.get("Id") and latest.get("Image") == image_id
            and latest.get("State", {}).get("Running") is True,
            "Deployment changed while recording. Wait for Jenkins to finish, then retry.")
    checks = ["clean_committed_source", "running_container", "immutable_image_id",
              "image_label_matches_git", "container_revision_matches_git", "health_matches_git",
              "version_matches_git", "visible_release", "stable_container_during_capture"]
    evidence = {
        "schema_version": 1,
        "verification": "passed",
        "phase": args.phase,
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_revision": revision,
        "release": release,
        "container_name": args.container,
        "container_id": container["Id"],
        "image_id": image_id,
        "image_reference": container.get("Config", {}).get("Image"),
        "base_url": args.base_url,
        "health": health,
        "runtime": version,
        "checks": checks,
    }
    if args.phase == "after":
        before_path = ROOT / "assignment5" / "reports" / "evidence" / "before.json"
        require(before_path.is_file(), "Record the before snapshot first.")
        try:
            before = json.loads(before_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise VerificationError("The before snapshot cannot be read as JSON.") from error
        require(isinstance(before, dict) and before.get("verification") == "passed"
                and before.get("phase") == "before" and before.get("release") == "Demo release 1",
                "The baseline is not a valid verified before snapshot.")
        require(SHA.fullmatch(before.get("git_revision", ""))
                and IMAGE_ID.fullmatch(before.get("image_id", "")),
                "The before snapshot has invalid revision or image identity.")
        require(revision != before["git_revision"], "Git revision did not change from before.")
        require(image_id != before["image_id"], "Docker image ID did not change from before.")
        evidence["previous_git_revision"] = before["git_revision"]
        evidence["previous_image_id"] = before["image_id"]
        evidence["checks"].extend(["git_revision_changed", "image_id_changed", "release_1_to_2"])
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("before", "after"))
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--container", default="skinlab-a5-demo")
    args = parser.parse_args()
    target = ROOT / "assignment5" / "reports" / "evidence" / f"{args.phase}.json"
    proof_target = target.with_name("proof.json")
    try:
        require(not target.exists(), f"{target.relative_to(ROOT)} already exists. Preserve it; remove it explicitly only to restart the demonstration.")
        if args.phase == "after":
            require(not proof_target.exists(), f"{proof_target.relative_to(ROOT)} already exists. Preserve the previous demonstration evidence.")
        evidence = snapshot(args)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as stream:
            json.dump(evidence, stream, indent=2)
            stream.write("\n")
        if args.phase == "after":
            proof = {
                "schema_version": 1,
                "verification": "passed",
                "captured_at_utc": evidence["captured_at_utc"],
                "before": {"git_revision": evidence["previous_git_revision"],
                           "image_id": evidence["previous_image_id"], "release": "Demo release 1"},
                "after": {"git_revision": evidence["git_revision"],
                          "image_id": evidence["image_id"], "release": evidence["release"]},
                "comparison": {"git_revision_changed": True, "image_id_changed": True,
                               "visible_release_changed": True},
                "evidence_files": ["before.json", "after.json"],
                "scope": "Verified deployment snapshots. Jenkins automatic build cause requires separate Jenkins evidence.",
            }
            with proof_target.open("x", encoding="utf-8") as stream:
                json.dump(proof, stream, indent=2)
                stream.write("\n")
    except (VerificationError, OSError, KeyError, TypeError, AttributeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: {args.phase} snapshot verified ({evidence['release']}).")
    print(f"Git revision: {evidence['git_revision']}")
    print(f"Image ID: {evidence['image_id']}")
    print(f"Saved: {target.relative_to(ROOT)}")
    if args.phase == "after":
        print("Verified: Git revision, Docker image ID and visible release all changed.")
        print(f"Saved: {proof_target.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
