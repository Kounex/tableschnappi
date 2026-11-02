#!/usr/bin/env bash
# Connected-cluster workshop bootstrap. See README.md before running.

set -Eeuo pipefail
trap 'echo "ERROR at line $LINENO; inspect oc get events -A --sort-by=.lastTimestamp" >&2' ERR

# Resolve repository paths independently of the caller's working directory.
ROOT=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)

# Environment overrides control the target project and optional workloads.
TIMEOUT=${TIMEOUT:-1800}
NAMESPACE=${NAMESPACE:-tableschnappi-workshop}
RHOAI_CHANNEL=${RHOAI_CHANNEL:-}
INSTALL_WORKSHOP=${INSTALL_WORKSHOP:-false}
MLFLOW_MANIFEST=${MLFLOW_MANIFEST:-$ROOT/infra/mlflow-workshop.yaml}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

if [[ ${1:-} == --help ]]; then
  cat <<'HELP'
Usage: [environment variables] bash infra/install-prerequisites.sh
Requires oc, jq, a logged-in cluster administrator, OCP 4.22, default storage.
RHOAI_CHANNEL: optional catalog channel; head must be RHOAI 3.5.x.
NAMESPACE: participant project (default tableschnappi-workshop).
MLFLOW_MANIFEST: reviewed MLflow CR (default local-storage workshop example).
INSTALL_WORKSHOP=true: also install chart; requires helm, MODEL_ENDPOINT,
MODEL_NAME and MLFLOW_URI. MODEL_ENDPOINT must accept unauthenticated requests
for this chart's guardrails. Existing model hosting is an input.
EVALHUB_MANIFEST: optional reviewed EvalHub CR for the participant namespace.
TIMEOUT: timeout in seconds per readiness phase (default 1800).
Installs cert-manager when absent and enables KServe for TrustyAI.
The script never installs GPU drivers, creates users, or removes components.
HELP
  exit 0
fi

# Validate local inputs before making any cluster changes.
[[ $# == 0 ]] || fail 'Unknown arguments (use --help)'

for cmd in oc jq; do
  command -v "$cmd" >/dev/null || fail "Install $cmd first"
done

[[ $TIMEOUT =~ ^[1-9][0-9]*$ ]] || fail 'TIMEOUT must be positive seconds'
[[ $NAMESPACE =~ ^[a-z0-9]([-a-z0-9]*[a-z0-9])?$ && ${#NAMESPACE} -le 63 ]] || fail 'Invalid namespace'
[[ $INSTALL_WORKSHOP == true || $INSTALL_WORKSHOP == false ]] || fail 'INSTALL_WORKSHOP must be true or false'
[[ -r $MLFLOW_MANIFEST ]] || fail 'MLFLOW_MANIFEST is not readable'

# Model and tracking endpoints are needed only for the optional Helm install.
if [[ $INSTALL_WORKSHOP == true ]]; then
  command -v helm >/dev/null || fail 'Install Helm first'
  : "${MODEL_ENDPOINT:?Set MODEL_ENDPOINT (without /v1)}" \
    "${MODEL_NAME:?Set MODEL_NAME}" \
    "${MLFLOW_URI:?Set MLFLOW_URI}"
  [[ $MODEL_ENDPOINT != */v1 && $MODEL_ENDPOINT != */ ]] || fail 'MODEL_ENDPOINT must have no trailing / or /v1'
fi

# Verify cluster identity, supported version, storage and catalog access.
oc whoami >/dev/null
[[ $(oc auth can-i '*' '*' --all-namespaces) == yes ]] || fail 'Cluster administrator access is required'
[[ $(oc whoami) != kubeadmin ]] || fail 'Use an identity-provider cluster administrator, not kubeadmin'

version=$(oc get clusterversion version -o jsonpath='{.status.desired.version}')
[[ $version == 4.22.* ]] || fail "Expected OCP 4.22.x; found $version"

oc get storageclass -o json | jq -e '
  any(.items[];
    .metadata.annotations["storageclass.kubernetes.io/is-default-class"] == "true"
  )
' >/dev/null || fail 'Configure a default dynamic storage class'

oc get catalogsource redhat-operators -n openshift-marketplace >/dev/null

# Resolve a channel from live catalog metadata, rather than assuming a name.
package=$(oc get packagemanifest rhods-operator -n openshift-marketplace -o json)
if [[ -z $RHOAI_CHANNEL ]]; then
  RHOAI_CHANNEL=$(jq -r '
    [.status.channels[]
      | select(.currentCSVDesc.version | test("^3\\.5\\."))
      | .name
    ] | sort | .[0] // empty
  ' <<<"$package")
fi

[[ -n $RHOAI_CHANNEL ]] || fail 'No channel with a 3.5.x head is available in redhat-operators'
csv=$(jq -r --arg channel "$RHOAI_CHANNEL" '
  .status.channels[]
  | select(.name == $channel)
  | select(.currentCSVDesc.version | test("^3\\.5\\."))
  | .currentCSV
' <<<"$package")
[[ -n $csv ]] || fail 'Selected channel does not currently offer 3.5.x'

# Reuse only an existing 3.5 installation in the expected operator namespace.
existing=$(oc get subscriptions -A -o json | jq -r '.items[] | select(.spec.name == "rhods-operator") | .metadata.namespace')
[[ -z $existing || $existing == redhat-ods-operator ]] || fail 'RHOAI subscription exists in another namespace'

if [[ -n $existing ]]; then
  installed=$(oc get subscription rhods-operator -n redhat-ods-operator -o jsonpath='{.status.installedCSV}')
  [[ $installed == rhods-operator.3.5.* ]] || fail "Existing installation $installed needs an administrator-reviewed upgrade"
else
  oc create namespace redhat-ods-operator --dry-run=client -o yaml | oc apply -f -

  # Keep future upgrades manual; the initial install plan is checked below.
  cat <<YAML | oc create -f -
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: rhods-operator
  namespace: redhat-ods-operator
spec: {}
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: rhods-operator
  namespace: redhat-ods-operator
spec:
  name: rhods-operator
  channel: $RHOAI_CHANNEL
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  startingCSV: $csv
  installPlanApproval: Manual
YAML
fi

# Approve only the initial plan containing the selected 3.5 CSV.
end=$((SECONDS + TIMEOUT))

while :; do
  installed=$(oc get subscription rhods-operator -n redhat-ods-operator -o jsonpath='{.status.installedCSV}')
  if [[ -n $installed ]] && [[ $(oc get csv "$installed" -n redhat-ods-operator -o jsonpath='{.status.phase}') == Succeeded ]]; then
    break
  fi

  plan=$(oc get subscription rhods-operator -n redhat-ods-operator -o jsonpath='{.status.installPlanRef.name}')
  if [[ -n $plan && -z $existing ]]; then
    oc get installplan "$plan" -n redhat-ods-operator -o json | \
      jq -e --arg csv "$csv" '
        .spec.clusterServiceVersionNames | index($csv) != null
      ' >/dev/null || fail 'Unexpected install plan; review manually'
    oc patch installplan "$plan" -n redhat-ods-operator --type=merge -p '{"spec":{"approved":true}}'
  fi

  (( SECONDS < end )) || fail 'Timed out waiting for RHOAI operator'
  sleep 10

done

# KServe supplies the InferenceService CRD required by TrustyAI. Install its
# certificate dependency before enabling either component. Reuse existing
# cert-manager installations without changing their subscription or settings.
if ! oc get crd certificates.cert-manager.io >/dev/null 2>&1; then
  cert_subscriptions=$(oc get subscriptions -A -o json | jq '
    [.items[] | select(.spec.name == "openshift-cert-manager-operator")] | length
  ')

  if [[ $cert_subscriptions == 0 ]]; then
    oc create namespace cert-manager-operator --dry-run=client -o yaml | oc apply -f -

    cat <<'YAML' | oc create -f -
apiVersion: operators.coreos.com/v1
kind: OperatorGroup
metadata:
  name: cert-manager-operator
  namespace: cert-manager-operator
spec: {}
---
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: openshift-cert-manager-operator
  namespace: cert-manager-operator
spec:
  name: openshift-cert-manager-operator
  channel: stable-v1
  source: redhat-operators
  sourceNamespace: openshift-marketplace
  installPlanApproval: Automatic
YAML
  fi

  # CRDs may not exist yet, so poll for discovery before using oc wait.
  end=$((SECONDS + TIMEOUT))
  until oc get crd certificates.cert-manager.io >/dev/null 2>&1; do
    (( SECONDS < end )) || fail 'Timed out installing cert-manager; inspect its Subscription and InstallPlan'
    sleep 10
  done
fi

oc wait --for=condition=Established crd/certificates.cert-manager.io --timeout="${TIMEOUT}s"

# Admission needs a serving webhook, not just registered cert-manager CRDs.
end=$((SECONDS + TIMEOUT))
until oc get endpoints -A -o json | jq -e '
  any(.items[];
    (.metadata.name | test("cert-manager.*webhook")) and
    any(.subsets[]?; (.addresses // [] | length) > 0)
  )
' >/dev/null; do
  (( SECONDS < end )) || fail 'Timed out waiting for cert-manager webhook endpoints'
  sleep 10
done

# The operator must register the DSC API before components can be configured.
oc wait --for=condition=Established crd/datascienceclusters.datasciencecluster.opendatahub.io --timeout="${TIMEOUT}s"

dscs=$(oc get datasciencecluster -o json)
count=$(jq '.items | length' <<<"$dscs")
[[ $count -le 1 ]] || fail 'Multiple DataScienceClusters require manual reconciliation'

if [[ $count == 0 ]]; then
  oc create -f "$ROOT/infra/datasciencecluster.yaml"
  dsc=default-dsc
else
  dsc=$(jq -r '.items[0].metadata.name' <<<"$dscs")

  # Enable only required components; preserve all other existing settings.
  oc patch datasciencecluster "$dsc" --type=merge -p '{
    "spec": {
      "components": {
        "dashboard": {"managementState": "Managed"},
        "workbenches": {"managementState": "Managed"},
        "aipipelines": {
          "managementState": "Managed",
          "argoWorkflowsControllers": {"managementState": "Managed"}
        },
        "kserve": {"managementState": "Managed"},
        "trustyai": {"managementState": "Managed"},
        "mlflowoperator": {"managementState": "Managed"}
      }
    }
  }'
fi

# Include child component conditions on failure: DSC messages can hide the
# concrete missing prerequisite behind a generic PreConditionFailed reason.
if ! oc wait --for=jsonpath='{.status.phase}'=Ready "datasciencecluster/$dsc" --timeout="${TIMEOUT}s"; then
  oc get datasciencecluster "$dsc" -o yaml >&2 || true
  oc get trustyai.components.platform.opendatahub.io -o yaml >&2 || true
  oc get kserve.components.platform.opendatahub.io -o yaml >&2 || true
  fail 'OpenShift AI components did not become ready; inspect the conditions above'
fi

# Create MLflow only when absent so reruns preserve existing storage settings.
oc wait --for=condition=Established crd/mlflows.mlflow.opendatahub.io --timeout="${TIMEOUT}s"

if [[ $(oc get mlflows.mlflow.opendatahub.io -o json | jq '.items | length') == 0 ]]; then
  oc apply --dry-run=server -f "$MLFLOW_MANIFEST" >/dev/null
  oc create -f "$MLFLOW_MANIFEST"
fi

# Make the participant project visible in the OpenShift AI dashboard.
oc create namespace "$NAMESPACE" --dry-run=client -o yaml | oc apply -f -
oc label namespace "$NAMESPACE" opendatahub.io/dashboard=true --overwrite

# A supplied EvalHub manifest must pass admission before it is applied.
if [[ -n ${EVALHUB_MANIFEST:-} ]]; then
  oc apply --dry-run=server -n "$NAMESPACE" -f "$EVALHUB_MANIFEST" >/dev/null
  oc apply -n "$NAMESPACE" -f "$EVALHUB_MANIFEST"
fi

# Install the participant chart after shared platform components are configured.
if [[ $INSTALL_WORKSHOP == true ]]; then
  domain=$(oc get ingresses.config.openshift.io cluster -o jsonpath='{.spec.domain}')
  role=${MLFLOW_ROLE:-mlflow-operator-mlflow-integration}
  oc get clusterrole "$role" >/dev/null

  helm upgrade --install tableschnappi "$ROOT/charts/tableschnappi" -n "$NAMESPACE" \
    -f "$ROOT/charts/tableschnappi/values-workshop.yaml" \
    --set-string "rhoai.appsDomain=$domain" --set-string "rhoai.mlflowUri=$MLFLOW_URI" \
    --set-string "rhoai.mlflowIntegrationClusterRole=$role" \
    --set-string "model.endpoint=$MODEL_ENDPOINT" --set-string "model.name=$MODEL_NAME" \
    --wait --timeout "${TIMEOUT}s"
fi

# Show the shared services for the remaining readiness and access checks.
oc get pods -n redhat-ods-applications
oc get routes -n redhat-ods-applications

printf '\nBootstrap finished. Complete access, model, EvalHub and notebook checks in infra/README.md.\n'
