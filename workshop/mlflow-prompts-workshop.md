# Change the prompt, observe the difference

Use your own MLflow workspace. The restaurant loads
`restaurant-assistant-prompt@active`. Creating a version and activating it are
separate actions. Existing `baseline` and `active` aliases initially select
the starting version.

This registered text supplies the restaurant agent's **system prompt**: its
instructions for answers, tool use and reservations. The assistant adds
date/seasonal context and the conversation before calling the model. Editing
this prompt changes the restaurant's behavior; it does not move the agent into
the notebook or remove reservation checks enforced in code.

## 1. Keep a baseline

In MLflow, open Prompts → `restaurant-assistant-prompt`. Note the version with
the `active` alias. Chat about the menu and save its trace.
For the guided one-hour lab, [run the baseline batch now](mlflow-evaluation-workshop.md#1-record-the-baseline),
before creating/activating your candidate. Skip this step if you already
recorded it at minutes 22–27.

## 2. Create a version

Create a new version from the current prompt. Keep its booking/tool rules and
literal `{date}` / `{time}` placeholders. Append:

```text
Format every response with three short sections: Answer, Evidence, Next step.
In Evidence, distinguish facts returned by restaurant tools from information
that you cannot verify. Do not invent stock levels or chef confirmations.
```

Use a commit message explaining your hypothesis. Compare the two versions.
The current app uses Python-style placeholders; do not add arbitrary braces
or replace this text prompt with a multi-message chat template.

## 3. Activate and test

Assign/move the **active** alias to the new version in MLflow. Creating a new
version alone does not change this workshop deployment.
Start a New chat and repeat the menu and stock questions. The workshop disables
alias caching: no assistant restart should be needed. Check the response's
prompt version, open the trace, and find its linked prompt/version and model
input. The application also adds date/seasonal context to the registered text.
If you see fallback or an unexpected version, stop and ask your instructor.

Did the format change? Is the answer better supported? Try an unrelated
question. Model behavior can vary; one attractive answer is insufficient.
Keep this candidate active while you [record and compare its five cases](mlflow-evaluation-workshop.md#2-record-the-candidate).
The notebook sends requests to the restaurant API; the restaurant's LangGraph
agent executes them using the selected system prompt.

## 4. Restore

After the candidate comparison finishes, move **active** back to the version
selected by **baseline**. Start a fresh chat
and verify the original version appears. Your candidate versions and traces
remain available. Do not delete prompts or reset your project.
