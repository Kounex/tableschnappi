# 04 — Compare the candidate

Your candidate should now be selected by the **active** alias. Compare it with
the baseline you recorded in step 02, using exactly the same five questions.

## 1. Run one candidate batch

Return to **comparison.ipynb**. Set `VARIANT = 'candidate'` and `RUN_BATCH = True`,
then execute the batch cell once. Set `RUN_BATCH = False` afterwards.

Keep the active alias and guardrail policy unchanged while it runs. The helper
never publishes a prompt or moves an alias. It stops if the app uses a fallback,
a different prompt version, or returns a trace that cannot be read.

## 2. Compare the evidence

In MLflow's **restaurant-workshop-comparison** experiment, select your baseline
and candidate runs. Compare the tool-expectation rate, section-format rate and
mean duration. Open **comparison.json** and follow the restaurant trace links.

These are diagnostic checks, not factual-accuracy scores. A tool expectation
can be wrong, and latency includes the app's HTTP request path. Assess quality
yourself:

- Did the candidate improve the menu answer and cite actual tool evidence?
- Did it still clarify missing booking information?
- Did it admit that live stock information was unavailable?
- Did the new format improve usefulness or just add words?

A green trace or a higher formatting score alone does not make a better answer.
This small comparison uses MLflow runs; it does not add an LLM judge.

## 3. Restore the baseline prompt

In MLflow, move **active** back to the version selected by **baseline**. Start a
New chat and check that the original prompt version appears. Keep the candidate
versions, feedback and comparison runs as evidence.

**Optional next:** [05 — Try a guardrail](05-guardrails.md). Keep the baseline
prompt fixed during that exercise so you can isolate the policy's effect.
Otherwise [finish and wrap up](README.md#finish-and-restore).
