# 01 — Meet your restaurant and follow a trace

## 1. Find your application

1. Open your instructor's **restaurant URL**. Check that its hostname contains
   your project, `tableschnappi-userN`. Each participant has a separate app.
2. Open **Sakura** and its chat panel. Look at the menu and restaurant information
   first: the assistant should ground its answers in this application.
3. Open your instructor's **MLflow URL** in another tab. Complete the normal
   OpenShift sign-in, then choose workspace **tableschnappi-userN**. Open
   **Experiments → restaurant-chatbot-traces → Traces**. It may be empty until
   you send the first question.

If you only have the OpenShift Console URL, choose your project and open
**Networking → Routes**. Use the route ending in `frontend` for the restaurant.
Ask your instructor for the MLflow link rather than using another user's workspace.
You do not need the workbench yet.

## 2. Predict, then chat

Start a **New chat** for each question. Predict whether it needs a tool:

| Question | Look for |
|---|---|
| “I would like to book a table.” | Does it ask for missing details before reserving? |
| “Which vegetarian main dishes are on your menu? Please check the menu.” | A menu lookup and evidence supporting its answer |
| “Exactly how many fresh truffles are left in your kitchen right now?” | No inventory tool exists: does it admit that limit? |

Use the same restaurant for all exercises. Record what your model actually does;
tool selection and wording can vary. Only confirm a reservation if you intend
to create synthetic demo state.

## 3. Open the trace

Click **Open trace** below a response; sign in if requested. If only a trace
ID appears, find it in your experiment's **Traces** tab. Allow a few seconds
for export and check the workspace selector.

Expand the trace tree and follow the turn from input to answer:

- **Chat turn:** your question, response and total duration.
- **Graph/model spans:** system instructions, messages, generated answer/tool calls
  and token usage when the provider supplies it.
- **MCP tool span:** tool name, arguments, result and duration. For the menu
  question, find `get_menu` and check which answer details its result supports.
- **Guard spans:** the request passes through the shield; its input policy starts
  empty. Later you will enable a check and compare the execution path.

LangGraph autologging captures framework/model execution. Explicit application
spans name the overall chat turn and MCP request boundary. The MCP span does
not instrument every backend operation; its result preview can be truncated.
Which stage took longest? Did a correct clarifying answer need a tool?

## 4. Give feedback

Rate one answer with thumbs up/down in the restaurant. Refresh its trace and
find the **user_rating** feedback assessment. A failed save should offer retry.
A green trace means execution completed; it does not establish correctness.

**Quick extra:** ask “What is the current wait time? Please check.” Find the
other tool and compare its result and duration with the menu trace.

**Next:** [02 — Change the system prompt](02-prompts.md).
