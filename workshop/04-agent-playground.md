# 04 — Open your workbench and run your own agent

So far, the restaurant service ran the agent and MLflow explained its behavior.
Now you will run and edit a small **LangGraph agent inside your workbench**.
Its traces go to a separate experiment in the same namespace-authorized workspace.

## 1. Open JupyterLab

1. Open your instructor's **OpenShift AI** link and sign in as `userN`.
2. Choose **Projects → tableschnappi-userN → Workbenches**.
3. Find workbench **userN**. It should be **Ready**. If stopped, select **Start**
   and wait; ask your instructor if it remains queued or fails to start.
4. Click **Open** / the open icon beside that workbench. Complete OpenShift's
   authorization screen if shown. JupyterLab should open without a separate token.
5. In JupyterLab's left file browser, open **tableschnappi → workshop →
   agent-playground.ipynb**. Choose the **Python 3** kernel if asked.

Do not create another workbench or clone another repository. The model key,
MLflow connection/auth and notebook packages are already supplied by the lab.
If the files or imports are missing, ask your instructor to check the source/image.
See the [OpenShift AI workbench instructions](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/3.5/html/working_on_projects/using-project-workbenches_projects)
if the dashboard layout differs.

## 2. Run the setup

Read the introduction, then execute each setup/function cell in order with
**Shift+Enter**. The first cell should print your workspace and experiment
**restaurant-agent-playground**. Never print the entire environment or API key.
The final execution cell defaults to `RUN_AGENT=False`, so **Run all** initially
makes no model calls.

In the controls cell, keep the menu question and both tracing switches enabled.
Set a short `LABEL`, then set `RUN_AGENT=True` in the final cell and run it once.
Open **restaurant-agent-playground → Traces** in MLflow and find its printed
trace ID or `playground.label` tag.

## 3. Compare tracing modes

Change the **controls cell**, execute it, then rerun the **final execution cell**.
The agent rebuilds from the current controls; you do not need a kernel restart.
Use a new `LABEL` for each experiment and keep the question fixed.

| AUTOLOG | MANUAL_SPANS | Find in MLflow |
|---|---|---|
| `True` | `True` | Overall turn, graph/model execution, explicit MCP span and format function |
| `True` | `False` | Framework/model spans; custom boundaries disappear |
| `False` | `True` | Custom turn/tool/format spans; model internals disappear |
| `False` | `False` | The agent answers, but creates no new trace |

Autologging observes supported framework calls. Manual spans explain your own
steps and give the MCP HTTP boundary a meaningful name, inputs and result.
Neither the workbench annotation nor simply importing MLflow instruments all code.

## 4. Toggle MCP and explore

Set **USE_MCP=False**, return both tracing controls to `True`, and repeat the
menu question. The notebook skips MCP discovery and execution; the model has
no live menu data. Compare its grounding, tool spans and number of model calls.
Then re-enable MCP and ask for current wait time. Tool choice is a model decision,
so inspect what happened instead of assuming a particular path.

If time remains, pick one change:

- Change `SYSTEM_PROMPT` to request **Answer / Evidence / Next step**. Find the
  changed model input and compare the answer.
- Edit `format_answer` or add a manual span around a small validation step.
  Rerun that function cell, then the final cell, and inspect its inputs/outputs.
- Change temperature modestly and repeat a fixed question. Record variation;
  one answer is not an evaluation score.

This is a separate agent. It calls the model directly, uses read-only MCP tools,
and **does not run through the restaurant's NeMo shield**. Editing it does not
change the restaurant prompt alias, guardrail ConfigMap or frontend behavior.
The core exercise is tracing plus the MCP toggle; extra runs share the room's
model quota. The notebook bounds model/tool calls to stop runaway loops.

## 5. Finish

Set `RUN_AGENT=False`. Keep your traces and edits. Confirm the restaurant's
prompt and empty guardrail policy were restored in the earlier guides. Share
one observation about what autologging captured and what needed a manual span.
