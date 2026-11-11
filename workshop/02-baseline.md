# 02 — Record the baseline

Before changing the system prompt, save how the restaurant answers five fixed
questions. Later you will compare your candidate against this starting point.

## 1. Open the notebook

In this folder, open **comparison.ipynb**. Run the setup cell. It displays your
MLflow workspace and active prompt version. If either is unexpected, ask your
instructor before continuing.

The notebook calls the restaurant API. The agent and model calls still execute
in the restaurant stack; you are not starting a second agent in the workbench.

## 2. Run one baseline batch

Set `VARIANT = 'baseline'` and `RUN_BATCH = True`, then execute the batch cell
once. It sends five independent chats with fresh sessions. Set
`RUN_BATCH = False` afterwards to avoid accidental repeat calls.

Keep the active prompt and guardrail policy unchanged while the batch runs.
A prompt fallback, mismatched version or unreadable trace stops the batch.

## 3. Find the evidence

In MLflow open **restaurant-workshop-comparison**. Find the baseline run's
prompt version, metrics and **comparison.json**. The table contains the
questions, answers, tool names and links to the real restaurant traces.

Keep this notebook open. Do not edit the test questions: the candidate should
answer the same cases. Creating prompt versions and moving aliases happens in
the MLflow UI, not in the comparison notebook.

**Next:** [03 — Change the system prompt](03-prompts.md).
