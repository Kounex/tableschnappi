# 02 — Prompt, repeat, compare

This exercise stays in the restaurant and MLflow browser tabs. The restaurant
loads `restaurant-assistant-prompt@active` as its **system prompt**: instructions
for answers, tool use and reservations. The assistant adds date/seasonal context
and the conversation. Booking checks enforced in code remain in place.

## 1. Save a baseline

In your MLflow workspace, open **Prompts → restaurant-assistant-prompt**. Note
which version has **active** and **baseline**; they should initially agree.
If they do not, ask your instructor before changing anything.

In the restaurant, start a **New chat for each question** and save the answer
and **Open trace** link in a small table or your notes:

| Question | Baseline answer / trace | Candidate answer / trace |
|---|---|---|
| “Which vegetarian main dishes are on your menu? Please check the menu.” | | |
| “Exactly how many fresh truffles are left in your kitchen right now?” | | |

Check the response's prompt version and its linked prompt in MLflow. Leave the
NeMo input policy empty for both versions so you change one thing at a time.
These two questions are enough for the timed exercise; add a booking question
if you have time. No notebook or batch runner is needed.

## 2. Create a version

Create a **new version** from the current prompt. Keep the booking/tool rules
and literal `{date}` / `{time}` placeholders. Append:

```text
Format every response with three short sections: Answer, Evidence, Next step.
In Evidence, distinguish facts returned by restaurant tools from information
that you cannot verify. Do not invent stock levels or chef confirmations.
```

Use a commit message explaining what you expect to change, then compare the
versions' text in MLflow. The current app uses Python-style placeholders;
do not add arbitrary braces or replace the text with a multi-message template.

## 3. Activate and repeat

Move the **active** alias to your new version. Publishing a version alone
does not change the application. The workshop resolves this alias on every
turn; no assistant restart should be needed.

Start fresh chats and repeat **exactly the same two questions**. Add the
candidate answers/trace links to your table. Check the response's prompt version,
the trace's linked prompt and the actual system input. If you see built-in
prompt fallback or the wrong version, ask your instructor before comparing.

Compare a baseline/candidate trace pair side by side:

- Did the answer adopt the headings? Did they make it more useful?
- Does the menu answer cite actual tool evidence? Did tool selection change?
- Does it admit the unavailable stock data instead of inventing it?
- Did model calls, token usage or duration change? One call is not a benchmark.

A formatting improvement alone does not prove factual accuracy. Model variation
can also explain differences; one pair provides a hypothesis, not a guarantee.
You can rate the candidate and find its `user_rating` in MLflow as before.

## 4. Restore

Move **active** back to the version selected by **baseline**. Start a New chat
and verify the original version appears. Keep both versions and their traces.
The restaurant agent has run in its normal service throughout this exercise;
MLflow stored/activated the prompt and recorded the evidence.

**Next:** [03 — Add a guardrail](03-guardrails.md). Keep the baseline prompt
fixed to isolate the policy change.
