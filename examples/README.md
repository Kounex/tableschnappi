# Additional development examples

These examples cover capabilities beyond the one-hour event lab. They are kept
for developers extending the application; attendees use `workshop/README.md`.
They retain their own setup assumptions and are not the event's prescribed path.

| Topic | Files | Purpose |
|---|---|---|
| Connectivity | `01_connect_and_explore.ipynb` | Inspect individual service connections |
| Direct-model prompt comparisons | `02_prompt_tuning.ipynb`, `prompt-tuning-workshop.ipynb` | Explore model calls independently of the restaurant's end-to-end comparison |
| Guardrail evaluation | `03_guardrails_and_eval.ipynb`, `04_guardrails_eval_automated.ipynb`, `guardrails-eval.py` | Broader evaluation and judge examples |
| Red teaming | `05_garak_redteam.ipynb` | Optional garak tooling |
| Native evaluation jobs | `06_evalhub_native.ipynb` | EvalHub API examples |
| Evaluation pipelines | `eval_pipeline.py` | Compile/submit a Kubeflow pipeline |
| Seasonal RAG | `generate_sekki_pdfs.py`, `sekki_data.py`, `sekki_ingest.py`, `sekki_pipeline.py` | Generate and ingest seasonal restaurant knowledge |
| Independent prompt setup | `seed-mlflow-prompts.py` | Seed prompts for the standalone examples; the event uses the chart's seed hook |

Notebook dependencies are in `requirements-notebooks.in`. Pipeline compilation
uses `requirements-pipeline.in` in its own environment. Run scripts from the
repository root using `python examples/<name>.py`; related generated PDFs/fonts
remain beside these examples and are ignored by Git.
