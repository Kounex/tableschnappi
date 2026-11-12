# Prepare and reset the MLflow workshop

The attendee path lives only in [workshop/README.md](../workshop/README.md).
Cluster installation, project setup, accounts and full teardown live in
[the infrastructure repository](https://github.com/Kounex/summit-connect-mlflow-lab-infra).
This guide covers application-specific preparation and rehearsal.

## Deliver the workshop revision

Use `charts/tableschnappi/values-multi-user.yaml` plus site values. Supply built
image digests; a source change does not rebuild deployed images. For this
revision, rebuild the **workbench** image: the agent notebook adds pinned
LangChain/LangGraph dependencies in `workshop/helpers/requirements.txt`.
Build `workshop/helpers/Dockerfile.workbench` with `workshop/helpers/` as context.
The Dockerfile checks for dependency conflicts introduced over its pinned RHOAI
base. Application images do not need a rebuild for these guide/notebook changes.

Pin `workbench.repoRef` / the source ConfigMap archive to the workshop revision.
A new source ref does not overwrite an existing notebook PVC. Follow the infra
runbook's explicit participant reset/recreate for a clean demo, after exporting
anything to retain. Recreate its external pull grants and source/Secret inputs
as the runbook describes. Do not delete shared MLflow data for a content update.

The multi-user profile pins a source revision containing these guides. The
infra runbook may intentionally remain pinned to the previously deployed version
until the new image has been built and rehearsed; update both source and image
inputs together when rolling this workshop out.

Required chart configuration:

- Endpoint/model and the namespace-local existing Secret. Workbench environment
  supplies `MODEL_BASE_URL`, `MODEL_NAME`, `OPENAI_API_KEY`, `MCP_URL`, and
  `MODEL_EXTRA_BODY` from the same values used by the restaurant. The Qwen
  request option can be disabled with `model.extraBody: false` for other models.
- Shared tracking URI and public `rhoai.mlflowUiUrl`, including its `/mlflow`
  prefix. The native Notebook annotation injects MLflow auth/connection settings;
  the notebook keeps TLS verification enabled and never needs a pasted token.
- `assistant.promptUri: prompts:/restaurant-assistant-prompt@active` and
  `assistant.promptCacheTtlSeconds: 0`. The seed only creates missing aliases;
  verify **active** and **baseline** both select the intended starting version.
- `guardrails.enabled: true`, `guardrails.shieldsEnabled: true`, and initial
  `rails.input.flows: []`. Reapplying Helm can overwrite live policy edits;
  do not reapply the release during attendee exercises.
- Real participant login names `user1`–`user50` and matching demo passwords.

## Prepare links and the empty guardrail baseline

Give each attendee their account, project, restaurant, MLflow, OpenShift AI and
OpenShift Console URLs. Link the [workshop overview](../workshop/README.md) in the
joining instructions. The first three guides require no workbench.

Before the session, inspect each project's guardrail ConfigMap. Preserve its
model stanza and set `rails.input.flows: []`; remove any exercise-specific
moderation prompt if restoring the original baseline. Preserve `rails.co` and
its refusal message. Restart NeMo after edits and warm it before attendee use.
The infrastructure runbook has a native warmup Job and batch entry command.
Do not equate a ready pod or an assistant refusal with successful guard enforcement.

During the guardrail exercise, warm NeMo again after the attendee's policy
restart. Confirm one menu request passes and one off-topic request blocks,
then check the actual restaurant trace's `guardrails.outcome`. Errors/fail-open
are failures to investigate. After restore, restart/warm the empty policy again.

## Rehearse

Follow the [attendee schedule](../workshop/README.md) as two real identities:

1. Find the assigned restaurant and MLflow workspace; use the answer's trace
   link and confirm persisted feedback. Test foreign-workspace denial.
2. Record the two baseline questions in notes, create/activate a new prompt,
   repeat the same questions, inspect version/lineage and restore **active**.
3. Starting from the empty policy, follow the ConfigMap guide exactly. Reserve
   the full 15-minute guardrail slot, including restart, warmup and restore.
4. Only then open the workbench and run `agent-playground.ipynb`. Test both,
   autolog-only, manual-only and tracing-off modes, and MCP on/off. Verify
   notebook traces land in `restaurant-agent-playground`, while restaurant
   traces stay in `restaurant-chatbot-traces` in the same workspace.
5. Confirm notebook prompt/MCP edits do not change the restaurant's active
   prompt or policy. Notebook model calls bypass the restaurant's NeMo shield.
6. Check simultaneous workbench capacity and external model quota. One agent
   turn can need multiple model calls. Keep exploration to a few labeled runs;
   shorten optional questions before reducing the guardrail exercise.

## Reset without losing evidence

Restore **active** to the version selected by **baseline**; restore the original
empty NeMo policy, restart/warm it, and start a New restaurant chat. Set notebook
`RUN_AGENT=False`. Retain traces, feedback, prompt versions and notebooks.
A backend restart resets in-memory restaurant state. Namespace/PVC deletion is
a destructive content reset; follow the infra runbook when that is intended.
Shared MLflow history survives participant namespace recreation.
