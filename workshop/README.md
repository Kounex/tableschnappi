# Start here: explore the restaurant with MLflow

Your instructor provides your account, restaurant URL, OpenShift AI URL and
MLflow URL. Demo credentials match: username `user1`, password `user1`
(and likewise `user2:user2` through `user50:user50`). Use your own
project/workspace, `tableschnappi-userN`.
Read the numbered guides in order. Open `comparison.ipynb` only when steps
02 and 04 tell you to; `helpers/` contains implementation files you do not need
to open or run.

Keep the restaurant, MLflow and your workbench open in separate tabs. Use
synthetic data. The learning loop is **predict → chat → inspect → change → compare**.

## Your hour

| Time | Exercise | What to look for |
|---|---|---|
| 0–5 min | Sign in, open the restaurant, MLflow workspace and workbench | All three belong to your `userN` project |
| 5–15 min | [Follow three chat turns](01-traces.md) | Clarification, a menu tool call, and uncertainty about unavailable information |
| 15–18 min | [Rate an answer and inspect its feedback](01-traces.md#3-give-feedback) | Technical success and answer quality are different |
| 18–23 min | [Record the five-case baseline](02-baseline.md) in the notebook | Save evidence before changing anything |
| 23–33 min | [Create and activate a system-prompt version](03-prompts.md) in MLflow | Repeat a question; find the new version and changed instructions in its trace |
| 33–40 min | [Record the candidate and compare](04-compare.md) | Inspect several answers and tool choices, not just the best example |
| 40–55 min | [Enable and test guardrails](05-guardrails.md), steps 1–5 | Edit the policy, restart/warm NeMo, and compare allowed/blocked requests and traces |
| 55–60 min | Restore the baseline and share one finding | Keep versions, traces and comparisons as evidence |

Keep the candidate active until its comparison batch finishes. Leave guardrails
unchanged for both batches. Before the guardrail exercise, return the prompt
to baseline and keep it fixed while comparing policy behavior. Guardrails are
a normal part of this lab. Use one comparison batch per version and inspect
one representative difference to protect the full 15-minute guardrail slot.
Additional test questions and the competitor challenge are optional extensions.

## What runs where?

| Place | Role |
|---|---|
| MLflow UI | Inspect traces/feedback; create and compare prompt versions; move `active` to a version |
| Restaurant stack | Run the LangGraph agent, call the model and MCP tools, and log the actual chat traces |
| Workbench notebook | Send test questions to that restaurant API and record comparison results |

`restaurant-assistant-prompt` supplies the restaurant agent's **system prompt**.
The assistant combines it with date/seasonal context and the conversation.
Moving `active` changes the version used when the agent next handles a turn;
the agent still executes in the restaurant stack. The notebook neither runs a
replacement agent nor changes the alias. Reservation checks enforced in code
remain in place when you edit the prompt.

Use `comparison.ipynb` for this lab.

## Finish and restore

Move `active` back to the version selected by `baseline`. If you changed the
NeMo policy, restore its saved text and follow the guardrail guide's restart and
warmup instructions. Start a New chat and verify the baseline prompt version.
Do not delete your namespace, workbench or MLflow history.

You have completed the core lab when you can show a tool span, identify the
prompt version, find persisted feedback, and explain a baseline/candidate
difference using the same test question. You should also be able to demonstrate
one allowed and one guard-blocked request and identify their different trace paths.

In the workbench, open `tableschnappi/workshop/`. Dependencies, the model and
MLflow authentication should already be configured. Ask your instructor if a
trace cannot be opened or the chat reports a built-in prompt fallback.
You do not need another model key or an MCP server for these exercises.
