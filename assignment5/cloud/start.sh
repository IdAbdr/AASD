#!/bin/sh
# Run from the repository root: sh assignment5/cloud/start.sh
set -eu
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)

if [ -z "${CODESPACE_NAME:-}" ] || [ -z "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-}" ]; then
    printf '%s\n' 'ERROR: Run this command in the GitHub Codespaces terminal.' >&2
    exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
    printf '%s\n' 'ERROR: Docker is unavailable. Use the default GitHub Codespaces environment.' >&2
    exit 1
fi
if ! docker info >/dev/null 2>&1; then
    printf '%s\n' 'ERROR: The Codespaces Docker daemon is not ready. Check docker info before retrying.' >&2
    exit 1
fi
if ! docker compose version >/dev/null 2>&1; then
    printf '%s\n' 'ERROR: Docker Compose is unavailable in this Codespaces environment.' >&2
    exit 1
fi
if [ ! -S /var/run/docker.sock ]; then
    printf '%s\n' 'ERROR: /var/run/docker.sock is missing. This lab requires the default local Codespaces daemon.' >&2
    exit 1
fi

JENKINS_PUBLIC_URL="https://${CODESPACE_NAME}-8080.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/"
export JENKINS_PUBLIC_URL
docker compose -f "$script_dir/compose.yaml" config -q
docker compose -f "$script_dir/compose.yaml" up -d --build
printf '\nJenkins URL: %s\n' "$JENKINS_PUBLIC_URL"
printf 'Application URL after a successful deployment: https://%s-8000.%s/\n' \
    "$CODESPACE_NAME" "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN"
printf '%s\n' 'Keep forwarded ports 8080 and 8000 Private in the Ports tab.'
printf '%s\n' 'Wait for Jenkins to finish starting, then retrieve its initial administrator password:'
printf '%s\n' 'docker compose -f assignment5/cloud/compose.yaml exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword'
