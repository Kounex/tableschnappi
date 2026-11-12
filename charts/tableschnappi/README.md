# Deploying a multi-user workshop

Use one release per participant namespace. `values-multi-user.yaml` is a small
profile for a restaurant, notebook-only workbench, shared namespace-authorized
MLflow and NeMo. The lab does not register a separate AI asset. Copy it to your ignored
`my-values.yaml`, replace the example domain/model/image references and set
`workbench.name`/`workbench.username` to the participant's OpenShift identity.

## Shared platform versus application release

A platform administrator supplies OpenShift AI with workbenches, MLflow and
TrustyAI managed, a ready shared MLflow server/storage, participant projects,
quotas/LimitRanges, network policy and any cross-project image-pull grants.
Label projects `opendatahub.io/dashboard: "true"` for dashboard discovery. The
chart does not install cluster operators, create identity-provider accounts,
build application images or manage shared MLflow infrastructure.

The release owns its restaurant Deployments/Services/Route, NeMo CR/config,
workbench PVC/Notebook/service account, local RoleBindings and optional AI asset
registration. Native operators reconcile the Notebook and NeMo children.
The profile disables per-user pipelines so a workbench does not imply another
DSPA, MinIO and MariaDB installation. Existing `values-workshop.yaml` retains
its pipelines-enabled default.

## Render, review, install

Create the external model Secret from a private file, not an inline Helm value:

```bash
oc create secret generic model-api-key -n tableschnappi-user1 \
  --from-file=api_key=/private/path/model-api-key
helm template tableschnappi charts/tableschnappi -n tableschnappi-user1 \
  -f my-values.yaml > /tmp/user1.yaml
# Inspect the rendered YAML, then install:
helm upgrade --install tableschnappi charts/tableschnappi -n tableschnappi-user1 \
  -f my-values.yaml --wait --timeout 15m
```

Build/publish images separately and set `components.<name>.image` to a complete
`registry/repository@sha256:...` reference. The legacy shared
`image.registry`/`components.<name>.repository`/`image.tag` values still work when
the full-reference override is empty. `model.secretKey` defaults to `token` for
compatibility; use `api_key` to match the native custom endpoint Secret.
`model.extraBody: false` disables Qwen-specific request options for other APIs.

Repeat in each participant's namespace with their identity values. The profile
requires an installer authorized to create the local role grants; in particular,
`workbench.grantEdit: true` grants the human and notebook SA edit in that namespace.
It grants no cluster-wide role binding. Assistant/seed and workbench use separate
SAs, bound to the operator's MLflow integration ClusterRole in their own namespace.
Verify real participant SSO and foreign-workspace denial before the event.

## MLflow and participant content

The Notebook's top-level `opendatahub.io/mlflow-instance` annotation enables
native connection/auth injection. It does not instrument arbitrary notebook code.
The assistant and seed hook explicitly select the release namespace as their
workspace. The initial seed registers a prompt only if absent; upgrades preserve
participant versions and propagate authorization/service errors instead of
mistaking them for a missing prompt.

`workbench.repoRef` accepts a full source commit. Initial Git fetch uses that
revision; existing PVC content is preserved on restart, including participant
edits. Failed first fetches can retry. The selected workbench image needs Bash
and Git. Git credentials use an askpass helper and are not embedded into the
saved remote URL.

For an offline/prepackaged lab, set `workbench.sourceConfigMap` to an existing
ConfigMap with `source.tar.gz` and `SOURCE_COMMIT`. Optionally list notebook/helper
filenames under `workbench.seedFiles`; these keys are copied from the same
ConfigMap only when absent. The source archive must not include credentials.
Changing source values/ConfigMaps does not overwrite existing participant files.
Export notebooks before a deliberate PVC reset.

## AI asset and guardrails

The multi-user lab leaves `aiAsset.enabled: false`: its restaurant and NeMo use
model values/Secrets directly. For other use cases, `aiAsset.enabled: true`
creates the native project ConfigMap
`gen-ai-aa-custom-model-endpoints` with the same endpoint/model/Secret reference.
Enable the RHOAI 3.5 dashboard custom endpoint feature separately. This is
Technology Preview and configures AI assets/Playground discovery; it does not
proxy model traffic, watch/reconfigure the application or create a local served
model. It owns that fixed-name ConfigMap: enable it only in a dedicated lab
project without an existing UI-managed endpoint registry.

`genaiStudio.enabled` remains off in the multi-user profile because its existing
MCP registration is a shared singleton. No MaaS/Kuadrant gateway is installed.

`guardrails.enabled: true` keeps NeMo available. The multi-user profile sets
`shieldsEnabled: true` and retains the empty initial NeMo policy, matching
`workshop/03-guardrails.md`. Its assistant-settings ConfigMap controls
`GUARDRAILS_ENABLED`; restart the assistant after changing that setting. After enabling
policies/restarting NeMo, warm it with allowed/blocked requests before a chat and
inspect traces/logs for fail-open: the existing 15-second timeout/fail-open policy
and workshop TLS settings are unchanged by this chart PR.

## Upgrade and cleanup

Version 0.2 moves persistent model Secrets, assistant SAs and RoleBindings from
hooks into normal release resources. Wait/seed/model-check Jobs run post-install
and post-upgrade, after those resources exist. Normal persistent resources are
then tracked for `helm uninstall`; hook Jobs use delete policies, except the
existing garak result Job retained for inspection.

For a **0.1 release**, inspect the old persistent hook resources before upgrading.
If they lack Helm ownership metadata, explicitly adopt only this release's old
assistant SA, MLflow RoleBinding and chart-created model Secret. For each owned
resource use the following metadata (replace resource/name/release/namespace):

```bash
oc label RESOURCE NAME -n NAMESPACE app.kubernetes.io/managed-by=Helm --overwrite
oc annotate RESOURCE NAME -n NAMESPACE \
  meta.helm.sh/release-name=RELEASE meta.helm.sh/release-namespace=NAMESPACE --overwrite
```

Never adopt a supplied `model.existingSecret` or another release's resources.
Do not delete a running SA/Secret to get past an ownership error. Existing
DSPA resources must be assessed/backed up before turning pipelines off on an
old release; the multi-user profile is intended for new notebook-only releases.
For the event's current plain-apply deployment, there is no Helm release to
upgrade: plan a separate ownership/PVC migration or reset, after merge.

```bash
helm uninstall tableschnappi -n tableschnappi-user1 --wait
```

Export participant files first: the release owns the workbench PVC. If garak
was enabled, inspect/export and delete its retained hook Job separately. Supplied
Secrets/ConfigMaps and the participant namespace stay outside release ownership.
Shared MLflow history/storage and cross-project pull grants are also external;
remove them through the platform runbook when the event ends.

## Validation

```bash
helm lint charts/tableschnappi
python3 charts/tableschnappi/tests/test_workshop.py
```

Regression checks need PyYAML and Helm, and cover all 50 namespaces, token/key
consumers, normal resource ownership/post-hook order, MLflow opt-out, notebook
source pin/retry/edit preservation and prompt seed preservation/error handling.
Cluster admission tests do not replace a full install/upgrade/uninstall rehearsal.

### Guided MLflow workshop

The multi-user profile supports the [attendee lab](../../workshop/README.md).
It uses native MLflow prompt versions and an `active` alias, with alias caching
set to zero for the lab. `rhoai.mlflowUiUrl` supplies browser trace links; it is
separate from the tracking URI. Missing UI configuration leaves a copyable
trace ID. Follow [instructor preparation](../../docs/INSTRUCTOR.md) before
allocating the roster. Existing workbench content is preserved on upgrades.

### Workbench environment and image

No attendee needs to enter a model key, MLflow token or service URL. The
[Notebook template](templates/workbench/notebook.yaml) and native AI controller
provide these settings to the Python process:

| Setting | Supplied by |
|---|---|
| `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_AUTH` | Native Notebook annotation `opendatahub.io/mlflow-instance: mlflow`; auth mode is `kubernetes-namespaced` |
| MLflow bearer token | Kubernetes projects the workbench service account token at `/var/run/secrets/kubernetes.io/serviceaccount/token`; the MLflow SDK reads it, including rotation |
| `MLFLOW_WORKSPACE` | Helm release namespace, for example `tableschnappi-user1` |
| `OPENAI_API_KEY` | `secretKeyRef` to `model.existingSecret`, key `model.secretKey` |
| `MODEL_BASE_URL`, `MODEL_NAME` | `model.endpoint` + `/v1`, and `model.name` |
| `MODEL_EXTRA_BODY` | `model.extraBody`; enables/disables the optional Qwen request setting |
| `MCP_URL`, `RESTAURANT_API_URL`, `GUARDRAILS_URL` | Helm computes namespace-local service DNS for this release |
| `MLFLOW_UI_URL` | `rhoai.mlflowUiUrl`, for browser navigation |

The chart also creates the workbench service account and namespace-local
MLflow integration RoleBinding. Human browser SSO and the notebook's service
account are separate identities with access to the same workspace. An environment
variable selects a workspace; RBAC determines permission to use it.

For example, a rendered Notebook contains the following pieces (excerpt):

```yaml
apiVersion: kubeflow.org/v1
kind: Notebook
metadata:
  name: user1
  namespace: tableschnappi-user1
  annotations:
    opendatahub.io/mlflow-instance: mlflow
spec:
  template:
    spec:
      serviceAccountName: user1
      containers:
        - name: user1
          # The prepared image digest is supplied as workbench.image.
          env:
            - name: MLFLOW_WORKSPACE
              value: tableschnappi-user1
            - name: MODEL_BASE_URL
              value: https://model.example.com/v1
            - name: MODEL_NAME
              value: example-model
            - name: OPENAI_API_KEY
              valueFrom:
                secretKeyRef:
                  name: endpoint-api-key-1
                  key: api_key
            - name: MCP_URL
              value: http://tableschnappi-mcp.tableschnappi-user1.svc.cluster.local:3000/mcp
            - name: RESTAURANT_API_URL
              value: http://tableschnappi-backend.tableschnappi-user1.svc.cluster.local:3001
```

This is an explanatory excerpt, not another manifest to apply. MLflow URI/auth
are added by OpenShift AI after the Notebook is created, rather than copied into
this template. The notebook checks configuration without displaying credentials.
It does not set `MLFLOW_TRACKING_TOKEN` or ask attendees to paste a token.

The **Notebook CR is YAML**; the **Jupyter notebook is a source file** at
`workshop/agent-playground.ipynb`. The init container seeds pinned source onto
the workbench PVC. The image contains Python/Jupyter and dependencies; it does
not contain participant secrets or overwrite edited notebooks.

The prepared image recipe is
[`workshop/helpers/Dockerfile.workbench`](../../workshop/helpers/Dockerfile.workbench).
It extends a digest-pinned Red Hat RHOAI Python 3.12 data-science workbench image
and installs [`requirements.txt`](../../workshop/helpers/requirements.txt).
The [infra repository](https://github.com/Kounex/summit-connect-mlflow-lab-infra)
currently builds it with native `BuildConfig/tableschnappi-workbench` in
`tableschnappi-demo`, stores it in the integrated registry and sets the resulting
digest as `workbench.image`. The application GitHub image workflow currently
publishes the service images, not this workbench image.
