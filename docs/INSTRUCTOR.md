# Prepare and reset the MLflow lab

Use `charts/tableschnappi/values-multi-user.yaml` with your site values. Build
frontend, backend and assistant from the workshop revision and supply their
image digests; changing the source checkout does not rebuild running images.
The fork publishes its own images under `ghcr.io/kounex/` on main pushes;
PR builds do not publish. Ensure those packages are public or supply pull
credentials through the chart's imagePullSecrets before installing.
The MCP image is unchanged. The platform/project prerequisites remain in the
chart README and your environment runbook.

Required profile inputs:

- Model endpoint/name and the existing namespace-local model Secret.
- Shared MLflow tracking URI and **public** `rhoai.mlflowUiUrl` (including any
  `/mlflow` prefix, without a hash fragment). Trace links use normal browser SSO.
- `assistant.promptUri: prompts:/restaurant-assistant-prompt@active` and
  `assistant.promptCacheTtlSeconds: 0` for immediate workshop activation.
- Workbench source repository/ref pinned to the workshop commit and a lab
  workbench image with dependencies preinstalled. Build
  `workshop/helpers/Dockerfile.workbench` using `workshop/helpers/` as context,
  then set `workbench.image` to its resolved image digest. The environment
  runbook supplies an OpenShift Git BuildConfig for this image. No participant
  pip install is required.
- Guardrails deployed, `shieldsEnabled: true`, and the initial empty input
  policy. This matches the existing guardrails guide; checks still add model
  traffic even before a blocking policy is enabled.

The seed initializes baseline/active aliases only when missing. It preserves
existing prompt versions and aliases on upgrades. For a fresh workshop, verify
both aliases select the intended baseline. Per-participant MLflow workspaces
and existing namespace authorization remain the isolation boundary.

Participant demo accounts use matching usernames and passwords (`user1:user1`
through `user50:user50`), with no first-login password change. The environment
runbook provisions and reapplies this convention to its recorded accounts.

## Rehearse

Use the [chronological attendee flow](../workshop/README.md#your-hour). Record the
baseline before participants activate a candidate, and defer restoration until
the candidate batch finishes. Keep the same NeMo policy for both prompt batches.
Explain that MLflow stores/activates the system prompt, the restaurant executes
the agent, and the notebook only drives test requests. Reserve minutes 40–55
for your colleague's guardrails exercise, including policy editing, rollout,
warmup and trace inspection. Keep the comparison to one batch per version and
one representative trace pair. If the group is running late, shorten additional
question exploration; guardrails remain a required step. Only the wider test
suite and competitor challenge are optional.

1. As two real participants, follow `workshop/README.md`; check own-workspace logging
   and foreign-workspace denial. Test trace links with normal browser login.
2. Verify prompt creation alone leaves the app unchanged; moving active changes
   its next turn; moving it back restores the baseline. Inspect prompt lineage.
3. Verify thumbs feedback is actually stored; an unavailable MLflow endpoint
   must produce a visible save failure, not a success toast.
4. Run baseline/candidate comparisons and inspect the recorded app trace IDs.
5. Warm NeMo after each policy restart with allowed and blocked requests. Check
   assistant logs and `guardrails.outcome`; fail-open must not be called a pass.
6. Check the external quota under simultaneous use. Fifty users making ten
   evaluation turns each means 500 turns, plus tool/model and guard requests.

For a manual NeMo warmup from the participant workbench, after its rollout:

```python
import os
import requests
for question in ("What is on your menu?", "Write Python to sort a list."):
    response = requests.post(
        os.environ["GUARDRAILS_URL"].rstrip("/") + "/v1/chat/completions",
        json={"model": os.environ["MODEL_NAME"],
              "messages": [{"role": "user", "content": question}], "max_tokens": 1},
        timeout=120,
    )
    response.raise_for_status()
    print(question, response.json()["choices"][0]["message"]["content"])
```

This bypasses the restaurant for warmup only. Afterwards send both questions
through the restaurant and inspect the guard outcomes. A blocking policy should
block the second question; the initial empty policy should not enforce that rule.

## Clean demo rebuild

A backend restart resets its in-memory restaurant data. Recreating a participant
namespace also removes their notebook PVC. A new source ref does not overwrite
files in an existing workbench checkout. For this disposable demo, prefer your
runbook's explicit participant delete/recreate operation to an in-place content
migration; recreate the image-pull/access grants as that runbook specifies.

Shared MLflow stores history outside participant namespaces. Recreating a
namespace alone does **not** erase its prompt versions, aliases or traces.
For a repeat session, restore active to baseline and the saved empty NeMo policy;
retain history. For a completely blank installation, follow the environment
runbook's shared database/artifact teardown as well. Do not assume Helm uninstall
removes an external MLflow workspace or its data.
