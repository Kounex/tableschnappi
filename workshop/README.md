# Explore the restaurant with MLflow

Your instructor provides your account, restaurant URL, OpenShift AI URL and
MLflow URL. Use your own project/workspace, `tableschnappi-userNN`.
Keep the restaurant and MLflow open in separate tabs. Use synthetic data.

| Time | Exercise |
|---|---|
| 5 min | Sign in, open the restaurant and your MLflow workspace |
| 17 min | [Follow a chat turn and rate an answer](mlflow-tracing-workshop.md) |
| 15 min | [Change and restore the restaurant prompt](mlflow-prompts-workshop.md) |
| 13 min | [Compare five questions](mlflow-evaluation-workshop.md) |
| 7 min, optional | [Try a guardrail](guardrails-workshop.md), steps 2–4 with an instructor-prepared policy |
| 3 min | Restore the baseline and share one finding |

For the comparison exercise, record the baseline batch before changing your
prompt, then return to record the candidate batch. Leave guardrails unchanged
until both batches finish. The full guardrails guide and its competitor
challenge can also be completed after the session.

In the workbench, open `tableschnappi/workshop/`. Dependencies, the model and
MLflow authentication should already be configured. Ask your instructor if a
trace cannot be opened or the chat reports a built-in prompt fallback.
You do not need another model key or an MCP server for these exercises.
