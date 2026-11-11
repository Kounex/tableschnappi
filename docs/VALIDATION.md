# Guided lab validation

Checked locally on 2026-11-11. This is not an event-cluster deployment report.

| Check | Result |
|---|---|
| Helm lint and all-flags render | Pass |
| Chart regression suite | 11 tests pass, including all 50 namespace/identity mappings and alias preservation |
| Assistant regression suite | 7 tests pass: per-turn and concurrent prompt resolution, fallback visibility, blocked-turn metadata, trace URL, feedback failure/retry and guard outcome distinctions |
| Backend HTTP regression | Pass: upstream save failure and unreachable assistant both reach the caller |
| Frontend production build and backend TypeScript check | Pass |
| Four container builds and clean Compose start | Pass; restaurant menu request traversed frontend/backend/assistant/MCP with tracing disabled, as the default local profile specifies |
| Real local MLflow integration | Pass with SDK/server 3.17.1: ten stored app traces, two prompt versions, active/baseline aliases, linked prompt lineage, native session metadata, feedback assessment and two comparison-table artifacts |
| Browser walkthrough | Pass: configured model, New chat, prompt version, trace deep link and stored-feedback confirmation; aborted feedback request showed retry and subsequently succeeded |

The local integration used the actual application services and a deterministic
OpenAI-compatible **model stub**. Its answers and token counts are synthetic;
it cannot establish Qwen quality or production latency. The local tracking
server used plain localhost authentication; OpenShift service-account injection
and workspace authorization still need testing on the event cluster.

Screenshots from that local test (not Qwen/event-cluster results):

![Restaurant trace link and prompt version](images/chat-trace.png)

![Matching MLflow trace, linked prompt and feedback](images/mlflow-trace.png)

## Repeatable repository checks

Install the assistant's pinned requirements in an isolated Python environment,
plus PyYAML. The existing Helm tests require Helm on PATH.

```bash
npm ci
npm run build -w packages/frontend
npx tsc --noEmit -p packages/backend/tsconfig.json
npx tsx --test packages/backend/test/feedback.test.ts
python -m unittest discover -s packages/mlflow-proxy/tests -v
python -m unittest discover -s charts/tableschnappi/tests -v
helm lint charts/tableschnappi -f charts/tableschnappi/values-multi-user.yaml
helm template lab charts/tableschnappi \
  -f charts/tableschnappi/values-multi-user.yaml \
  --set garak.enabled=true --set workbench.pipelines.enabled=true \
  --set genaiStudio.enabled=true > /tmp/all-features.yaml
```

The new `mlflow-lab.yml` workflow runs builds/type checking and the regression
suites. Existing project CI remains separate.

## Before the event

- Build/publish the workshop images and pin them in the site values.
- Recreate a two-participant pilot with fresh workbench content and verify its
  installed notebook dependencies before creating all 50 workbenches.
- Rehearse with the actual Qwen API and operator-managed MLflow server, normal
  participant browser SSO, and cross-workspace denial.
- Verify warmed NeMo allowed/blocked requests and restore through the Console.
- Test simultaneous external-model quota/capacity, participant reset and final
  teardown. Ten evaluation turns per attendee alone means 500 app turns.

These remain pending: the saved event-cluster login was expired during this
work. No cluster resources or event data were changed by this implementation.
