# Compare a change on five questions

A better-looking menu answer might hide a regression elsewhere. This exercise
calls the real restaurant API and logs a small comparison as MLflow runs;
it uses no additional LLM judge.

## 1. Record the baseline

Before changing your prompt, open `mlflow-evaluation.ipynb` in the workbench.
Run setup. Set `VARIANT = 'baseline'` and `RUN_BATCH = True`, then execute the
batch cell once. It makes five independent chats with fresh sessions.
Set `RUN_BATCH = False` afterwards to avoid accidental repeat calls.

Open `restaurant-workshop-comparison` in MLflow. The run contains prompt version,
metrics and `comparison.json`, with answers and links to the real app traces.

## 2. Record the candidate

Follow [the prompt exercise](mlflow-prompts-workshop.md) to activate your new
version. Return to the notebook, set `VARIANT = 'candidate'` and execute the
batch once. Leave the active alias and guardrails unchanged while it runs.
The helper never publishes a prompt or moves an alias. A fallback, different
version or unreadable trace stops the batch rather than reporting success.

## 3. Compare

Select the two runs and compare the tool-expectation rate, section-format rate
and mean duration. Inspect `comparison.json` and the individual chat traces.
These are diagnostic checks, not a factual-accuracy score. A tool expectation
can be wrong, and latency measures the app request, including its HTTP path.

Rate usefulness and grounding yourself. Did the candidate preserve clarification
and uncertainty? Do its Evidence sections agree with the tool results?
A higher formatting score alone does not make a better assistant.

**Challenge:** change one instruction, predict which cases should change,
and run another candidate batch. Keep the dataset fixed for a fair comparison.

Restore `active` to `baseline` when finished. Keep the comparison runs.
