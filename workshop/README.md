# Your restaurant, explained with MLflow

You have your own restaurant and MLflow workspace, `tableschnappi-userN`.
Your instructor supplies the **restaurant**, **OpenShift AI**, **MLflow** and
**OpenShift Console** links. Sign in as `userN` with the matching password
(for example, `user1:user1`). Use synthetic data throughout.

Start in the browser. Keep the restaurant and MLflow in separate tabs. Follow
the four guides in order; open the workbench only in the final exercise.
`helpers/` and `tests/` are implementation files; attendees do not run them.

| Time | Guide | What you learn |
|---|---|---|
| 0–15 min | [01 — Restaurant and traces](01-traces.md) | Find your app, chat, inspect model/tool calls and give feedback |
| 15–30 min | [02 — Prompt, repeat, compare](02-prompts.md) | Save a baseline, activate a system-prompt version, compare the same questions and restore |
| 30–45 min | [03 — Guardrails](03-guardrails.md) | Start with an empty policy, edit the ConfigMap, restart NeMo and compare allowed/blocked traces |
| 45–60 min | [04 — Your own agent](04-agent-playground.md) | Open the workbench; experiment with LangGraph, autologging, manual spans and MCP |

## The story

```text
Restaurant browser → Backend → LangGraph assistant → Model
                                     ↓
                                MCP → Restaurant data
                                     ↓
                           Traces / prompts / feedback → MLflow
```

The restaurant assistant uses your namespace's MCP service for live menu/wait
information. MLflow lets you see its execution and change the system prompt
behind `restaurant-assistant-prompt@active`. NeMo can block a request before
that assistant runs. A successful trace does not establish a correct answer.

At the end you will run a **separate agent inside the workbench** and apply the
same ideas in editable Python. It uses the same model and read-only restaurant
MCP service, and logs to `restaurant-agent-playground` in your MLflow workspace.
The restaurant keeps logging to `restaurant-chatbot-traces`. Changing notebook
settings does not change the restaurant's prompt or guardrail policy.

## Finish

Keep your traces and prompt versions. Restore the restaurant's `active` alias
to `baseline` and restore the empty NeMo input policy as the guides explain.
You should be able to show a tool span, feedback, a prompt-version difference,
and an allowed/blocked trace pair, then explain how your notebook's tracing
settings changed what MLflow recorded. Do not delete your project or workbench.
