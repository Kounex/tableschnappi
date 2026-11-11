# Follow a restaurant conversation

You need your restaurant and MLflow workspace open. The experiment is
`restaurant-chatbot-traces`.

## 1. Predict, then chat

Start a **New chat** for each question. Predict whether it needs a tool:

1. “I would like to book a table.”
2. “Which vegetarian main dishes are on your menu? Please check the menu.”
3. “Exactly how many fresh truffles are left in your kitchen right now?”

Typical outcomes are a clarifying question, a menu lookup, and an admission
that live inventory is unavailable. Record what your model actually does.

## 2. Open the trace

Click **Open trace** below the response; sign in if requested. If only a trace
ID is shown, open the experiment's Traces tab and find that ID. Allow a few
seconds for export. Select your own workspace if needed.

Expand the graph/model/tool spans. Find the model input (including system
instructions), tool arguments, tool result and final answer. Which stage took
longest? Which answer details are supported by the menu result?

The manual MCP span shows the request boundary; it is not a trace of every
backend operation. Its result preview can be truncated. Token counts depend
on what the model provider returns.

## 3. Give feedback

Rate one answer with thumbs up/down in the restaurant. Refresh its trace and
find the `user_rating` feedback assessment. A failed save should offer retry.
A green trace means execution completed; it does not establish correctness.

**Challenge:** ask for current wait time. Find the different tool and compare
its output and duration with the menu trace. No tool call can also be correct:
a clarifying question or admission of uncertainty may need none.

Continue with [prompt versions](mlflow-prompts-workshop.md).
