#!/usr/bin/env bash
# Enable the RHOAI 3.5 model catalog. See model-catalog.md for prerequisites.
set -Eeuo pipefail

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

if [[ ${1:-} == --help ]]; then
  cat <<'HELP'
Usage: bash infra/enable-model-catalog.sh [--dry-run | --check]
Requires Bash, oc, jq and a logged-in cluster administrator.
Targets an existing RHOAI 3.5 installation with a managed, running dashboard.
--dry-run: validate both merge patches on the server without saving them.
--check: read-only configuration and readiness snapshot; exit 1 on failures.
APP_NAMESPACE: application namespace (default redhat-ods-applications).
REGISTRIES_NAMESPACE: used only if the DSC has no registriesNamespace
  (default rhoai-model-registries). An existing namespace setting is preserved.
TIMEOUT: seconds per readiness phase (default 600).
Uses the current oc context. Does not install or upgrade OpenShift AI.
HELP
  exit 0
fi

dry_run=false
check_only=false
if [[ ${1:-} == --dry-run ]]; then
  dry_run=true
  shift
elif [[ ${1:-} == --check ]]; then
  check_only=true
  shift
fi
[[ $# == 0 ]] || fail 'Unknown arguments (use --help)'

APP_NAMESPACE=${APP_NAMESPACE:-redhat-ods-applications}
REGISTRIES_NAMESPACE=${REGISTRIES_NAMESPACE:-rhoai-model-registries}
TIMEOUT=${TIMEOUT:-600}
[[ $TIMEOUT =~ ^[1-9][0-9]*$ ]] || fail 'TIMEOUT must be positive seconds'
for namespace in "$APP_NAMESPACE" "$REGISTRIES_NAMESPACE"; do
  [[ $namespace =~ ^[a-z0-9]([-a-z0-9]*[a-z0-9])?$ && ${#namespace} -le 63 ]] || fail 'Invalid namespace'
done
for cmd in oc jq; do
  command -v "$cmd" >/dev/null || fail "Install $cmd first"
done

oc whoami >/dev/null
[[ $(oc auth can-i '*' '*' --all-namespaces) == yes ]] || fail 'Cluster administrator access is required'

# Check the installed operator, rather than the catalog channel's future head.
operators=$(oc get clusterserviceversions.operators.coreos.com -A -o json)
jq -e '
  any(.items[];
    (.metadata.name | startswith("rhods-operator.")) and
    (.spec.version | test("^3\\.5\\.")) and .status.phase == "Succeeded"
  )
' <<<"$operators" >/dev/null || fail 'No successfully installed RHOAI 3.5.x operator found'

dscs=$(oc get datascienceclusters.datasciencecluster.opendatahub.io -o json)
[[ $(jq '.items | length' <<<"$dscs") == 1 ]] || fail 'Expected exactly one existing DataScienceCluster'
dsc=$(jq -r '.items[0].metadata.name' <<<"$dscs")
[[ $(jq -r '.items[0].spec.components.dashboard.managementState' <<<"$dscs") == Managed ]] || fail 'Enable the dashboard component and wait for it to be ready first'
registry_namespace=$(jq -r '.items[0].spec.components.modelregistry.registriesNamespace // empty' <<<"$dscs")
registry_namespace=${registry_namespace:-$REGISTRIES_NAMESPACE}

configs=$(oc get odhdashboardconfigs.opendatahub.io -n "$APP_NAMESPACE" -o json)
[[ $(jq '.items | length' <<<"$configs") == 1 ]] || fail 'Expected exactly one OdhDashboardConfig in APP_NAMESPACE'
config=$(jq -r '.items[0].metadata.name' <<<"$configs")

if [[ $check_only == true ]]; then
  failures=0

  check_json() {
    local description=$1 json=$2 filter=$3
    if jq -e "$filter" <<<"$json" >/dev/null; then
      printf 'PASS: %s\n' "$description"
    else
      printf 'FAIL: %s\n' "$description" >&2
      failures=$((failures + 1))
    fi
  }

  check_resource() {
    local description=$1 filter=$2 json
    shift 2
    if json=$(oc get "$@" -o json); then
      check_json "$description" "$json" "$filter"
    else
      printf 'FAIL: %s (could not read resource)\n' "$description" >&2
      failures=$((failures + 1))
    fi
  }

  printf 'Checking DSC %s, dashboard %s/%s, catalog namespace %s\n' \
    "$dsc" "$APP_NAMESPACE" "$config" "$registry_namespace"
  check_json 'Model registry component is Managed' "$dscs" \
    '.items[0].spec.components.modelregistry.managementState == "Managed"'
  # Accept an omitted flag's default, while rejecting an explicit null value.
  check_json 'Catalog menu is enabled' "$configs" \
    '(.items[0].spec.dashboardConfig // {}) | (has("disableModelCatalog") | not) or .disableModelCatalog == false'
  check_resource 'Model registry component has reconciled and is Ready' '
    (.items | length) == 1 and all(.items[];
      .status.observedGeneration == .metadata.generation and
      any(.status.conditions[]?; .type == "Ready" and .status == "True")
    )
  ' modelregistry.components.platform.opendatahub.io
  check_resource 'Catalog namespace is Active' '.status.phase == "Active"' \
    namespace "$registry_namespace"

  deployment_ready='
    (.spec.replicas // 1) as $desired |
    $desired > 0 and
    (.status.observedGeneration // 0) >= .metadata.generation and
    (.status.updatedReplicas // 0) == $desired and
    (.status.readyReplicas // 0) == $desired and
    (.status.availableReplicas // 0) == $desired and
    (.status.replicas // 0) == $desired
  '
  for deployment in rhods-dashboard model-registry-ui model-registry-operator-controller-manager; do
    check_resource "$APP_NAMESPACE/$deployment deployment is fully rolled out" \
      "$deployment_ready" deployment "$deployment" -n "$APP_NAMESPACE"
  done
  check_resource 'Model catalog deployment is fully rolled out' "$deployment_ready" \
    deployment model-catalog -n "$registry_namespace"

  # Check bundled catalog dependencies if present; external databases can be used.
  check_resource 'Additional catalog deployments are ready (if present)' \
    "all(.items[] | select(.metadata.name | startswith(\"model-catalog-\")); $deployment_ready)" \
    deployments -n "$registry_namespace"
  for source_config in default-catalog-sources model-catalog-sources; do
    check_resource "$source_config contains source definitions" \
      '(.data["sources.yaml"] // "" | length) > 0' \
      configmap "$source_config" -n "$registry_namespace"
  done
  check_resource 'Catalog Service has ports and a pod selector' \
    '(.spec.ports | length) > 0 and (.spec.selector | length) > 0' \
    service model-catalog -n "$registry_namespace"
  check_resource 'Catalog Service has ready endpoints' '
    any(.items[].endpoints[]?;
      .conditions.ready == true and .conditions.terminating != true and
      (.addresses | length) > 0
    )
  ' endpointslices.discovery.k8s.io -n "$registry_namespace" \
    -l kubernetes.io/service-name=model-catalog

  if (( failures > 0 )); then
    fail "$failures health check(s) failed; inspect component conditions, deployments and events"
  fi
  cat <<'CHECKED'
All configuration and Kubernetes readiness checks passed. No changes made.
Also verify model cards and source connection/visibility settings in the dashboard;
this snapshot does not test catalog API responses or browser access.
CHECKED
  exit 0
fi

dsc_patch=$(jq -nc --arg namespace "$registry_namespace" '{
  spec: {components: {modelregistry: {
    managementState: "Managed", registriesNamespace: $namespace
  }}}
}')
dashboard_patch='{"spec":{"dashboardConfig":{"disableModelCatalog":false}}}'

printf 'DSC: %s; dashboard config: %s/%s; registries namespace: %s\n' \
  "$dsc" "$APP_NAMESPACE" "$config" "$registry_namespace"
printf 'DSC merge patch: %s\nDashboard merge patch: %s\n' "$dsc_patch" "$dashboard_patch"

# Validate both changes before persisting either; the two writes are not atomic.
oc patch datascienceclusters.datasciencecluster.opendatahub.io "$dsc" \
  --type=merge -p "$dsc_patch" --dry-run=server -o name
oc patch odhdashboardconfigs.opendatahub.io "$config" -n "$APP_NAMESPACE" \
  --type=merge -p "$dashboard_patch" --dry-run=server -o name
if [[ $dry_run == true ]]; then
  echo 'Server dry-run passed. No configuration was saved.'
  exit 0
fi

oc patch datascienceclusters.datasciencecluster.opendatahub.io "$dsc" \
  --type=merge -p "$dsc_patch"
oc patch odhdashboardconfigs.opendatahub.io "$config" -n "$APP_NAMESPACE" \
  --type=merge -p "$dashboard_patch"

# Newly enabled components take time to create their namespace and deployment.
deadline=$((SECONDS + TIMEOUT))
until [[ -n $(oc get deployment model-registry-operator-controller-manager \
  -n "$APP_NAMESPACE" --ignore-not-found -o name) ]]; do
  (( SECONDS < deadline )) || fail 'Timed out waiting for model registry operator deployment; inspect DSC conditions'
  sleep 5
done
oc rollout status deployment/model-registry-operator-controller-manager \
  -n "$APP_NAMESPACE" --timeout="${TIMEOUT}s"

deadline=$((SECONDS + TIMEOUT))
until [[ -n $(oc get configmap model-catalog-sources -n "$registry_namespace" \
  --ignore-not-found -o name) ]]; do
  (( SECONDS < deadline )) || fail 'Timed out waiting for catalog sources; inspect modelregistry component conditions'
  sleep 5
done

oc get namespace "$registry_namespace"
oc get pods -n "$registry_namespace"
cat <<'NEXT'
Catalog configuration applied and source ConfigMap found.
Reload the dashboard and open AI hub > Models > Catalog.
Check Settings > Model resources and operations > Model catalog settings
for enabled sources, visibility filters and custom-source connection status.
Confirm that model cards load; backend resource checks do not verify the UI.
NEXT
