"""Exercise the live HTTP service and verify that the expected commit is running."""
import argparse
import io
import json
import time
import urllib.error
import urllib.request
from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--expected-revision")
    args = parser.parse_args()
    base = args.base_url.rstrip("/")
    last = None
    for _ in range(30):
        try:
            with urllib.request.urlopen(base + "/health", timeout=2) as response:
                health = json.load(response)
            break
        except (OSError, ValueError) as error:
            last = error
            time.sleep(1)
    else:
        raise RuntimeError(f"Service did not become ready: {last}")
    assert health["status"] == "ok", health
    if args.expected_revision:
        assert health["revision"] == args.expected_revision, health
    with urllib.request.urlopen(base + "/version", timeout=3) as response:
        version = json.load(response)
    assert version["revision"] == health["revision"]
    image = io.BytesIO()
    Image.new("RGB", (12, 8), (20, 80, 140)).save(image, format="PNG")
    request = urllib.request.Request(base + "/api/features", data=image.getvalue(),
                                     headers={"Content-Type": "image/png"})
    with urllib.request.urlopen(request, timeout=3) as response:
        features = json.load(response)
    assert features["mean_green"] == 80 and features["contrast"] == 0, features
    invalid = urllib.request.Request(base + "/api/features", data=b"invalid",
                                     headers={"Content-Type": "image/png"})
    try:
        urllib.request.urlopen(invalid, timeout=3)
        raise AssertionError("Invalid image was accepted")
    except urllib.error.HTTPError as error:
        assert error.code == 400, error.code
    print(json.dumps({"status": "passed", "revision": health["revision"],
                      "checks": ["health", "commit_identity", "runtime_version",
                                 "real_png_features", "invalid_input_rejection"],
                      "runtime": version}, indent=2))


if __name__ == "__main__":
    main()
