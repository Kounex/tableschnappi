#!/usr/bin/env bash
# Build the four application images, push to Quay, and update existing deployments.
set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  cat <<'EOF'
Usage: NAMESPACE=my-project ./scripts/build-push-rollout.sh

Requires an existing installation, podman login quay.io, and oc login.
Environment:
  NAMESPACE          Required OpenShift project
  QUAY_ORG           Quay organization or user (default: tableschnappi)
  DEPLOYMENT_PREFIX  Deployment name prefix (default: tableschnappi)
  TAG                Image tag (default: UTC timestamp)
  PLATFORM           Build platform (default: linux/amd64)
  ROLLOUT_TIMEOUT    Timeout per deployment (default: 180s)

Builds backend, frontend, mcp, and mlflow-proxy. Pushes all four before
updating deployments. Deploys by digest; unchanged images need no restart.
Existing model settings, credentials, and other deployment settings are kept.
EOF
  exit 0
fi
if (( $# )); then
  echo "Unknown argument: $1 (use --help)" >&2
  exit 1
fi

: "${NAMESPACE:?Set NAMESPACE to the existing OpenShift project}"
QUAY_ORG="${QUAY_ORG:-tableschnappi}"
DEPLOYMENT_PREFIX="${DEPLOYMENT_PREFIX:-tableschnappi}"
TAG="${TAG:-$(date -u +%Y%m%dT%H%M%SZ)}"
PLATFORM="${PLATFORM:-linux/amd64}"
ROLLOUT_TIMEOUT="${ROLLOUT_TIMEOUT:-180s}"
REGISTRY="quay.io/${QUAY_ORG}"

for command in podman oc; do
  command -v "$command" >/dev/null || {
    echo "Required command not found: $command" >&2
    exit 1
  }
done

cd "$(dirname "${BASH_SOURCE[0]}")/.."

# name|container|Dockerfile|build context
images=(
  'backend|backend|packages/backend/Dockerfile|.'
  'frontend|frontend|packages/frontend/Dockerfile|.'
  'mcp|mcp-server|packages/mcp-server/Dockerfile|.'
  'mlflow-proxy|mlflow-proxy|packages/mlflow-proxy/Dockerfile|packages/mlflow-proxy'
)

oc whoami >/dev/null
echo "Cluster: $(oc whoami --show-server)"
echo "Namespace: $NAMESPACE; registry: $REGISTRY; tag: $TAG"

# Check every target before spending time building or changing deployments.
for entry in "${images[@]}"; do
  IFS='|' read -r name container dockerfile context <<< "$entry"
  current=$(oc -n "$NAMESPACE" get deployment "${DEPLOYMENT_PREFIX}-${name}" \
    -o "jsonpath={.spec.template.spec.containers[?(@.name=='${container}')].image}")
  if [[ -z "$current" ]]; then
    echo "Container $container missing from deployment ${DEPLOYMENT_PREFIX}-${name}" >&2
    exit 1
  fi
done

for entry in "${images[@]}"; do
  IFS='|' read -r name container dockerfile context <<< "$entry"
  image="${REGISTRY}/tableschnappi-${name}:${TAG}"
  echo "Building $image"
  podman build --platform "$PLATFORM" --file "$dockerfile" --tag "$image" "$context"
done

digest_dir=$(mktemp -d)
trap 'rm -rf -- "$digest_dir"' EXIT
digests=()
for entry in "${images[@]}"; do
  IFS='|' read -r name container dockerfile context <<< "$entry"
  image="${REGISTRY}/tableschnappi-${name}:${TAG}"
  echo "Pushing $image"
  podman push --digestfile "$digest_dir/$name" "$image"
  digest=$(<"$digest_dir/$name")
  if [[ ! "$digest" =~ ^sha256:[0-9a-f]{64}$ ]]; then
    echo "Invalid pushed digest for $image: $digest" >&2
    exit 1
  fi
  digests+=("$digest")
done

for i in "${!images[@]}"; do
  IFS='|' read -r name container dockerfile context <<< "${images[$i]}"
  image="${REGISTRY}/tableschnappi-${name}@${digests[$i]}"
  echo "Deploying $image"
  oc -n "$NAMESPACE" set image "deployment/${DEPLOYMENT_PREFIX}-${name}" "$container=$image"
  oc -n "$NAMESPACE" rollout status "deployment/${DEPLOYMENT_PREFIX}-${name}" \
    --timeout="$ROLLOUT_TIMEOUT"
done

echo "All four deployments are ready."
echo "These image updates are applied directly; a later Helm upgrade uses its configured image values."
