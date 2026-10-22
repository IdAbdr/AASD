#!/bin/sh
# Promote only after the candidate passed smoke tests. Restore the old image if promotion fails.
set -eu
: "${RUNTIME_IMAGE:?RUNTIME_IMAGE is required}"
: "${TEST_IMAGE:?TEST_IMAGE is required}"
: "${SOURCE_REVISION:?SOURCE_REVISION is required}"
name=skinlab-a5-demo
previous=$(docker inspect --format '{{.Config.Image}}' "$name" 2>/dev/null || true)
mkdir -p reports
printf '%s\n' "$previous" > reports/previous-image.txt
docker rm -f "$name" >/dev/null 2>&1 || true
if docker run -d --name "$name" --restart unless-stopped -p 8000:8000 "$RUNTIME_IMAGE" > reports/deployed-container.txt    && docker run --rm --network "container:$name" "$TEST_IMAGE"        python ci/smoke.py --expected-revision "$SOURCE_REVISION" > reports/deployment-smoke.json; then
    printf '%s\n' "$RUNTIME_IMAGE" > reports/deployed-image.txt
    cat reports/deployment-smoke.json
else
    docker logs "$name" > reports/failed-deployment.log 2>&1 || true
    docker rm -f "$name" >/dev/null 2>&1 || true
    if [ -n "$previous" ]; then
        docker run -d --name "$name" --restart unless-stopped -p 8000:8000 "$previous"
        printf '%s\n' "Restored $previous; verify /health before use." > reports/rollback.txt
    fi
    exit 1
fi
