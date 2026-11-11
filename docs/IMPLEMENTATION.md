# From restaurant demo to a repeatable MLflow lab

The multi-user chart changes (`d030c5f`) and
[the guided lab PR](https://github.com/Kounex/tableschnappi/pull/1) are merged into
`Kounex/tableschnappi` main. The lab merge is `9c7c638`. Stefan's fork remains
upstream and its chart PR is separate. The new fork release still needs an
event-cluster rollout and rehearsal; merged code does not update running pods.

## The pitch in one minute

We have adapted the existing restaurant demo into a repeatable, one-hour
OpenShift AI lab for 50 named participants. Each participant gets their own
restaurant and workbench, while a shared MLflow server organizes their prompts,
traces and feedback in namespace-authorized workspaces. They first use the
restaurant and inspect what happened, then activate a new system-prompt version
and compare the same questions. They also enable NeMo guardrails and inspect
how a blocked request changes the execution path. YAML, Helm, pinned source and
image references, and explicit reset/teardown instructions make the setup
understandable and reproducible. Our fork lets us develop this event experience
independently and later propose selected changes back to Stefan.

## What we started with

Stefan's fork already supplied the restaurant frontend/backend, LangGraph
assistant, restaurant MCP tools, NeMo integration, MLflow autologging/manual
spans, a Helm chart and several exploratory notebooks. The guardrails guide
also came from our colleague. We built on those pieces; we did not create a
new restaurant, agent framework or tracing system.

## What changed and why it matters

| Area | Concrete change | Effect for the event |
|---|---|---|
| Installation | Extended the [Helm chart](../charts/tableschnappi/README.md) with a multi-user profile, namespace-local identities, existing Secret support, pinned images/source and ordered seed Jobs | The same chart can install one complete stack per participant |
| Prompt behavior | The [Python assistant](../packages/mlflow-proxy/app.py) accepts `PROMPT_URI`; the lab uses `@active` and resolves it once per turn | Publishing and activating are separate; a chat turn keeps one version; rollback means moving the alias |
| Prompt initialization | The [seed](../charts/tableschnappi/files/seed-mlflow.py) creates missing baseline/active aliases and retains existing versions/selections | Reapplying the installation does not silently reset a participant's work |
| Trace navigation | The assistant returns a trace URL and prompt metadata; [the chat widget](../packages/frontend/src/components/ChatWidget.tsx) displays them alongside the configured model and New chat | Attendees can go directly from an answer to its evidence and start independent comparisons |
| Reliable feedback | Python returns save errors, [Express forwards them](../packages/backend/src/assistant.ts), and the browser offers retry | A success message reflects a successful feedback write rather than hiding a failure |
| Trace context | Added native session metadata, prompt version/fallback tags, guard outcomes and explicit MCP exception status | Attendees can distinguish model behavior, tool errors and policy enforcement |
| Comparison | [One notebook helper](../workshop/helpers/lab_support.py) replays five fixed questions through the real restaurant API | Baseline/candidate results refer to the same application attendees use, not a replacement notebook agent |
| Learning path | [Five numbered guides](../workshop/README.md), one notebook and internal helpers; instructor/development material moved out | Attendees follow one route through the hour; guardrails has a required 15-minute slot |
| Delivery and checks | Fork-owned GHCR publishing plus [workshop CI](../.github/workflows/mlflow-lab.yml) | Image publishing is separate from the shared Quay organization; regression checks cover the added behavior |

The detailed sections below explain the mechanisms and their manual equivalents.
For a participant-facing explanation, start with [the workshop](../workshop/README.md).
For setup and warmup, use [the instructor guide](INSTRUCTOR.md).

## The platform work around the application

The environment runbook lives separately under `darmstadt-demo-2026-11-10/` in
our productivity workspace. It prepares the shared cluster and participant
projects; this application chart installs into that foundation.

| Runbook files | What they define | Why we chose it |
|---|---|---|
| `manifests/00-platform/` | Operator Subscription/OperatorGroup, managed DataScienceCluster components and dashboard configuration | OpenShift AI and the MLflow operator are reconciled by operators. The desired Subscription uses Automatic approval on `stable-3.5` |
| `manifests/10-images/`, `config/` | Git BuildConfigs with explicit Dockerfile/context paths, source commit and image locks | Builds have reviewable inputs; deployments can select immutable image digests |
| `manifests/20-mlflow/` | MLflow custom resource, PostgreSQL/PVC and ODF object-bucket storage | Share tracking metadata/artifacts across the event instead of installing 50 tracking servers |
| `manifests/30-participant/project/` | Namespace, service account, RoleBindings, quota, limits, ingress policy and image-pull grant | Repeatable separation and resource boundaries for `user01`–`user50`; project labels enable OpenShift AI discovery |
| Participant model configuration | External endpoint/model parameters and a namespace-local model Secret | Reuse the provided model API directly; unused AI asset registration has been removed from the lab |
| `scripts/` and `scripts/helpers/` | Thin batch entry commands, native `oc process` into server-side apply, Secret bootstrap and waits | Apply templates directly for a user range without generating 50 manifest trees; persistent configuration stays in YAML |
| `docs/TEARDOWN.md` | Exercise reset, participant deletion and full platform/storage removal | State clearly what is retained, including notebook PVCs and shared MLflow history |

Those runbook definitions include changes not yet reconciled onto the older live
deployment. In particular, its source lock still selects the earlier Stefan
revision. Moving to the merged fork requires new image/source selections and a
two-user delete/recreate pilot before applying the full roster.

The lab does not create an AI asset registration: it was a discovery entry
outside the request path, with no role in the attendee exercises. The restaurant
assistant and NeMo call the external API with the model Secret. The workbench
has model credentials for independent exploration, but the guided comparison
notebook only calls the restaurant API. Shared provider quota remains shared.
PostgreSQL is a single persistent lab Deployment, not an HA
operator-managed database. The runbook uses explicit applies; it does not add
a continuous GitOps controller.

The fork's image workflow publishes on `main` to `ghcr.io/kounex/…`, using
this repository's GitHub token. Pull requests build without publishing. Deploy
new application images by digest in site values; a source checkout alone cannot
replace a running image. Make the workshop packages pullable by the cluster,
either publicly or through the chart's imagePullSecrets setting.

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
| AI asset registration disabled in the lab | The restaurant does not consume it; endpoint/model configuration stays in Helm values and the Secret |
| Persistent Secrets/accounts/bindings as normal resources | Helm tracks them for uninstall; supplied external Secrets remain external |
| Wait/seed Jobs as post-install/post-upgrade hooks | Accounts and grants exist before the Jobs use them; seeding preserves existing prompts |
| Optional prepackaged source ConfigMap | Allows initial source delivery without Git access; existing PVC edits are preserved |

A RoleBinding refers to a ClusterRole but grants it only in the binding's
namespace. It is not a ClusterRoleBinding. The workbench container name must
also match the Notebook name: the native MLflow webhook locates that container
by name before injecting the connection/authentication environment. The chart
now follows that platform convention. Shared MLflow verifies namespace
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

The registered text is the restaurant agent's system prompt: instructions for
answering and choosing tools. Editing/activating it happens in MLflow. Execution
stays in the restaurant stack; the guided notebook only triggers restaurant API
requests. The application still enforces reservation rules in code.

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

Only the current numbered attendee guides and comparison notebook live in
`workshop/`; implementation files are in `workshop/helpers/`. Instructor setup
is in `docs/INSTRUCTOR.md`, and optional development examples are in `examples/`.
`comparison.ipynb` delegates HTTP/MLflow plumbing to `helpers/lab_support.py` and
reads the five questions in `helpers/restaurant-cases.json`.

It calls the backend's normal restaurant chat endpoint using `RESTAURANT_API_URL`.
Each case has a fresh session. It checks actual trace storage, tags app traces
with the case/variant, and logs a table and simple metrics in
`restaurant-workshop-comparison`. This is a small comparison using MLflow runs,
not an LLM judge or a separate implementation of the restaurant agent.

`workshop/helpers/Dockerfile.workbench` adds the pinned lab requirements to the
RHOAI data-science workbench image. The environment runbook builds it through
OpenShift and supplies its digest as `workbench.image`, so opening the notebook
does not require a manual package install. These packages do not replace the
native injected authentication.

The notebook reads the alias; it never publishes or activates prompts. Run the
baseline batch, change active in the MLflow UI, then run the candidate batch.
A fallback, mismatched version or unreadable trace stops the batch. Tool/format
checks are diagnostic expectations; participants assess answer quality themselves.

## 6. Guardrails use the existing operator and guide

Guardrails is a required part of the hour, using our colleague's guide and
policy examples. Its protected slot is minutes 40–55; only the wider test suite
and competitor challenge are optional. This is a policy experiment separate
from the system-prompt experiment.

The workshop profile connects the assistant shields from the start, while NeMo
starts with no input policy (`flows: []`). Participants edit the existing NeMo
ConfigMap through the Console and restart its Deployment, as the original guide
instructs. Editing that ConfigMap does not change the restaurant prompt registry.

After a restart, warm NeMo before judging a result. The assistant's existing
15-second timeout and fail-open policy remain: inspect the trace/logs rather
than treating a working chat as proof of enforcement. NeMo checks themselves
can call the model; their internal calls are not separately instrumented.
Restore the saved ConfigMap text and restart/warm NeMo to reset this exercise.

## The hour attendees experience

| Time | Activity | What they should be able to explain |
|---|---|---|
| 0–5 min | Open the app, MLflow and workbench | Which project/workspace is theirs |
| 5–18 min | Chat, inspect traces and give feedback | Why a tool was called, what it returned, and whether the answer was useful |
| 18–23 min | Record five baseline questions | Why evidence must be captured before changing the prompt |
| 23–33 min | Create/activate a system-prompt version | How MLflow's alias controls the restaurant's next turn |
| 33–40 min | Compare the candidate and restore the baseline prompt | What improved or regressed for the same question |
| 40–55 min | Apply, reload and test NeMo guardrails; inspect traces | Whether a request was blocked by policy and which stages were skipped |
| 55–60 min | Restore and discuss | How to return to the starting state without deleting evidence |

The notebook triggers requests to the restaurant. The LangGraph agent stays in
the restaurant stack. Neither the Notebook annotation nor the AI asset entry
turns arbitrary code into traced agent behavior; the existing and added SDK
instrumentation is what records it.

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
