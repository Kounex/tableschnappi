# What changed, why, and how to do it manually

This event fork is `Kounex/tableschnappi`. Stefan's fork remains upstream.
There are two separate changes: the earlier multi-user Helm work (commit
`d030c5f`, also proposed upstream as PR #1), and the guided MLflow lab built on it.
The application changes require new container images; a Git pull alone cannot
update a running restaurant.

The fork's image workflow publishes on `main` to `ghcr.io/kounex/…`, using
this repository's GitHub token. Pull requests build without publishing. The
inherited shared Quay destination is removed from this workflow. Deploy using
the resulting image digests in site values, not an assumption that the old
upstream images contain this fork's changes. Make workshop packages pullable
by the cluster, either publicly or with the chart's imagePullSecrets setting.

## 1. Helm is the participant application installer

Helm substitutes values into the YAML under `charts/tableschnappi/templates/`.
The OpenShift API creates those objects. Existing OpenShift AI operators then
reconcile the Notebook and NemoGuardrails custom resources into running pods.
Helm does not install the shared AI/MLflow operators or create participant logins.

The multi-user chart change adds these capabilities:

| Change | Purpose and runtime effect |
|---|---|
| `values-multi-user.yaml`, release namespace and workbench identity | One restaurant/workbench release per participant, with local service addresses |
| Workbench ServiceAccount and namespace RoleBindings | Human/workbench receive local edit and MLflow integration permissions; the assistant has its own service account |
| Notebook annotation `opendatahub.io/mlflow-instance: mlflow` | OpenShift AI injects connection/authentication for that MLflow instance; code must still instrument its calls |
| `MLFLOW_WORKSPACE` set to release namespace | Assistant, seed and workbench target the participant's namespace-authorized MLflow workspace |
| Optional per-user pipelines | The event disables DSPA/pipelines, avoiding a pipeline database/storage stack per person |
| Full image references and pinned workbench source | Images can use digests; fresh workbenches check out an exact source commit |
| Existing model Secret name/key | App, NeMo and workbench use a namespace-local Secret instead of placing keys in values |
| AI asset ConfigMap | Registers the external endpoint for project discovery; it does not proxy model requests or reconfigure the app |
| Persistent Secrets/accounts/bindings as normal resources | Helm tracks them for uninstall; supplied external Secrets remain external |
| Wait/seed Jobs as post-install/post-upgrade hooks | Accounts and grants exist before the Jobs use them; seeding preserves existing prompts |
| Optional prepackaged source ConfigMap | Allows initial source delivery without Git access; existing PVC edits are preserved |

A RoleBinding refers to a ClusterRole but grants it only in the binding's
namespace. It is not a ClusterRoleBinding. Shared MLflow verifies namespace
access: setting another workspace string alone does not authorize access.

## 2. Inspect and install one participant manually

The platform runbook supplies namespaces, quota, ingress policy, image-pull
grants, the identity provider and shared MLflow. A namespace needs the project
label `opendatahub.io/dashboard: "true"` for OpenShift AI discovery.

Copy `values-multi-user.yaml` to ignored `my-values.yaml`, then set your site
values: domain, model endpoint/name, Secret name/key, tracking/UI URLs, four
image digests and the workbench source commit. Use newly built images for the
three changed services; the MCP code is unchanged.

Create the model Secret from a private file after creating the namespace:

```bash
oc create secret generic model-api-key -n tableschnappi-user01 \
  --from-file=api_key=/private/path/model-api-key \
  --dry-run=client -o yaml | oc apply --server-side -f -

helm template tableschnappi charts/tableschnappi -n tableschnappi-user01 \
  -f my-values.yaml --set workbench.name=user01 --set workbench.username=user01 \
  > /tmp/user01.yaml
# Read the objects before installing:
helm upgrade --install tableschnappi charts/tableschnappi -n tableschnappi-user01 \
  -f my-values.yaml --set workbench.name=user01 --set workbench.username=user01 \
  --wait --timeout 15m
```

`helm template` is a preview. It also renders hook Jobs; blindly applying its
whole output does not reproduce Helm's dependency waits/hook order. To inspect
one resource's manual equivalent, use `--show-only`, for example:

```bash
helm template tableschnappi charts/tableschnappi -n tableschnappi-user01 \
  -f my-values.yaml --set workbench.name=user01 --set workbench.username=user01 \
  --show-only templates/workbench/notebook.yaml
```

You can apply individual rendered resources with `oc apply --server-side` in a
fresh project, waiting for prerequisites before running seed Jobs. Choose one
owner for the installation; do not interleave direct applies with an existing
Helm release. The supported event install command above handles that ordering.

Fifty users means repeating the same release in fifty prepared namespaces, not
creating fifty source YAML directories:

```bash
for number in {1..50}; do
  participant=$(printf 'user%02d' "$number")
  helm upgrade --install tableschnappi charts/tableschnappi \
    -n "tableschnappi-$participant" -f my-values.yaml \
    --set "workbench.name=$participant" --set "workbench.username=$participant" \
    --wait --timeout 15m || break
done
```

Each namespace must already have its model Secret and required platform grants.
This loop creates releases sequentially; it is not a transaction or load test.

## 3. Prompt versions now control the restaurant explicitly

Previously, every agent step loaded the hardcoded `@latest` prompt. Publishing
any version could change the running app after an SDK cache delay.

Now `PROMPT_URI` is configurable. The workshop profile selects
`prompts:/restaurant-assistant-prompt@active` and sets
`MLFLOW_ALIAS_PROMPT_CACHE_TTL_SECONDS=0`. The default profile retains `@latest`
and a 60-second alias cache. On the first agent step of a chat turn, the app
loads and formats the prompt and retains it for the remaining tool/model rounds
of that turn. The next turn resolves the alias again. Python ContextVar state
keeps simultaneous requests separate.

The seed creates missing `baseline` and `active` aliases. Existing aliases and
prompt versions are preserved. On an already-used workspace, a missing alias
initializes from its latest version: verify that version is the intended
starting point rather than assuming that namespace recreation cleared history.

Manual workflow in MLflow:

1. Open your workspace → Prompts → `restaurant-assistant-prompt`.
2. Create a new text version; preserve `{date}` and `{time}` placeholders.
3. Compare the text with the baseline. Creation alone leaves `active` unchanged.
4. Assign/move `active` to the candidate version and start a fresh restaurant chat.
5. Inspect its version and linked prompt in the trace.
6. Restore `active` to the version selected by `baseline`.

No application deployment is required for those alias changes. From an already
authenticated participant workbench, the SDK equivalent of step 4 is:

```python
import mlflow
mlflow.genai.set_prompt_alias(
    name="restaurant-assistant-prompt", alias="active", version=2,
)
```

Use your actual version number. Authentication/workspace come from the native
workbench integration. A registry/formatting failure still uses the built-in
prompt, but the response and trace now identify fallback. A guard-blocked turn
that never reaches the agent reports `not_used` instead of claiming a version.

## 4. The restaurant exposes the evidence

`packages/mlflow-proxy/app.py` retains the existing autologging and manual trace
boundaries. It additionally records native session metadata, prompt URI/version
and status, and guard outcomes (`skipped`, `allowed`, `blocked`,
`error_fail_open`). An MCP exception marks its tool span as an error. A successful
root trace still does not establish business correctness or guarantee every tool
succeeded; handled errors can be converted into an answer.

The assistant response retains `response`, `traceId` and `toolCalls`, and adds
`traceUrl`, `modelName` and `prompt` metadata. Its health response exposes the
configured model name. The frontend uses those fields for the model label,
prompt version and Open trace link. `rhoai.mlflowUiUrl` is the public browser URL,
including any `/mlflow` prefix; it is separate from the tracking URI. Workspace
and trace identifiers are included in the URL, with no embedded token. Browser
SSO and MLflow authorization still apply. Without a public UI URL, the response
shows a trace ID for manual lookup.

New chat clears browser conversation state and creates a new session ID. It
does not erase backend reservations, prompt versions or previous traces.

Feedback follows this path:

```text
thumbs → Express backend → Python assistant → MLflow feedback assessment
```

Previously both proxy layers could hide a logging failure. Now the Python API
returns a failed status, Express forwards it, and the browser displays a retry
message. Thanks appears only after a successful response. To verify manually,
rate an answer and find `user_rating` on the corresponding stored trace.

## 5. The workbench compares the actual application

The new guides live beside the existing guardrails guide in `workshop/`.
`mlflow-evaluation.ipynb` delegates HTTP/MLflow plumbing to `lab_support.py` and
reads the five questions in `data/restaurant-cases.json`.

It calls the backend's normal restaurant chat endpoint using `RESTAURANT_API_URL`.
Each case has a fresh session. It checks actual trace storage, tags app traces
with the case/variant, and logs a table and simple metrics in
`restaurant-workshop-comparison`. This is a small comparison using MLflow runs,
not an LLM judge or a separate implementation of the restaurant agent.

Install `workshop/requirements-lab.txt` in the workbench before the session,
or bake it into the selected workbench image; the instructor guide provides
the command. These packages do not replace the native injected authentication.

The notebook reads the alias; it never publishes or activates prompts. Run the
baseline batch, change active in the MLflow UI, then run the candidate batch.
A fallback, mismatched version or unreadable trace stops the batch. Tool/format
checks are diagnostic expectations; participants assess answer quality themselves.

## 6. Guardrails use the existing operator and guide

The workshop profile connects the assistant shields from the start, while NeMo
starts with no input policy (`flows: []`). Participants edit the existing NeMo
ConfigMap through the Console and restart its Deployment, as the original guide
instructs. Editing that ConfigMap does not change the restaurant prompt registry.

After a restart, warm NeMo before judging a result. The assistant's existing
15-second timeout and fail-open policy remain: inspect the trace/logs rather
than treating a working chat as proof of enforcement. NeMo checks themselves
can call the model; their internal calls are not separately instrumented.
Restore the saved ConfigMap text and restart/warm NeMo to reset this exercise.

## 7. Reset and teardown

For another exercise round, restore active to baseline, restore the original
NeMo policy, and start a New chat. This keeps comparison evidence.

For a clean participant rebuild, use the platform runbook's explicit namespace
cleanup/recreation. It removes the notebook PVC and in-memory restaurant state;
no content migration is needed for this disposable event. Recreate external
Secrets and pull/access grants before installing the new release. Merely changing
the workbench source ref preserves an existing checkout and will not refresh it.

For a Helm-only uninstall:

```bash
helm uninstall tableschnappi -n tableschnappi-user01 --wait
```

The release owns its notebook PVC. Namespace, supplied Secrets/source ConfigMaps,
cross-project grants and shared MLflow history are external. Namespace recreation
does not delete shared prompt versions/aliases/traces. Full shared metadata and
artifact deletion belongs to the platform teardown runbook.

## 8. What has been validated

See [VALIDATION.md](VALIDATION.md) for exact checks and remaining deployment gates.
The local model used for integration/browser checks is a deterministic stub;
those checks prove plumbing, not Qwen response quality or event-cluster capacity.
