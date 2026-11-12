# Third-Party Notices

TableSchnappi is licensed under the MIT Licence — see [LICENSE](LICENSE).
This file records third-party material and how it is licensed.

## Derived source

Material in this repository that originated elsewhere.

| File | Upstream | Licence | Notes |
|---|---|---|---|
| `charts/tableschnappi/templates/_helpers.tpl` | [helm/helm](https://github.com/helm/helm) `helm create` scaffold | Apache-2.0 | Standard generated template helpers, extended for this chart |
| `examples/04_guardrails_eval_automated.ipynb` | [rh-ai-quickstart/multi-agent-loan-origination](https://github.com/rh-ai-quickstart/multi-agent-loan-origination) | Apache-2.0 | Evaluation pattern adapted from `evaluations/evaluate_agent_v2.ipynb`; credit also retained in the notebook itself |

## Downloaded at build or run time

Not redistributed in this repository.

| Asset | Source | Licence | Where |
|---|---|---|---|
| Noto Sans JP | [google/fonts](https://github.com/google/fonts) | SIL OFL 1.1 | Fetched by `examples/generate_sekki_pdfs.py` and embedded into generated PDFs. OFL §1 expressly permits embedding, and does not make the resulting document OFL-licensed. No font binary is committed here. |

## Runtime dependencies

Installed from their upstream registries, not vendored. Exact resolved
versions for everything the containers run are pinned in `package-lock.json`
and the compiled `requirements.txt` files under `packages/`. The two
additional-example input files — `examples/requirements-notebooks.in` and
`requirements-pipeline.in` — are **not** compiled: they are installed into a
workbench interactively and carry loose ranges on purpose.

Notable, by component:

- **Assistant** (`packages/mlflow-proxy`): MLflow (Apache-2.0), LangChain and
  LangGraph (MIT), FastAPI (MIT), uvicorn (BSD-3-Clause), httpx
  (BSD-3-Clause), OpenAI Python SDK (Apache-2.0). With
  `INCLUDE_GARAK=true` it also pulls NVIDIA garak (Apache-2.0) and PyTorch
  (BSD-3-Clause), the latter from the PyTorch CPU index.
- **Backend** (`packages/backend`): Express (MIT), Socket.IO (MIT).
- **MCP server** (`packages/mcp-server`): Model Context Protocol SDK (MIT),
  zod (MIT).
- **Frontend** (`packages/frontend`): React and react-router-dom (MIT),
  socket.io-client (MIT), react-markdown (MIT), **lucide-react (ISC)**,
  Tailwind CSS, Vite and PostCSS (MIT).
- **Guided agent workbench** (`workshop/`): MLflow (Apache-2.0), LangChain and
  LangGraph (MIT), OpenAI Python SDK (Apache-2.0), requests (Apache-2.0).
  Direct versions are pinned in `workshop/helpers/requirements.txt`; the notebook
  and minimal stateless MCP client are original project content.
- **Additional examples** (`examples/`): kfp (Apache-2.0), Docling (MIT), transformers
  (Apache-2.0), pandas and numpy (BSD-3-Clause), matplotlib (PSF-style),
  seaborn (BSD-3-Clause), plotly (MIT), ipywidgets (BSD-3-Clause),
  fpdf2 (LGPL-3.0, used as an unmodified dependency only).

Everything above is permissively licensed except fpdf2 (LGPL-3.0), which is
used unmodified as a dependency, and the base images below.

Container base images carry their own distribution licences:
`node:20-alpine` and `nginxinc/nginx-unprivileged` (Alpine/BusyBox, GPL-2.0),
`python:3.11-slim` (Debian userland), `registry.access.redhat.com/ubi9/python-311`
(Red Hat UBI terms).

## Documentation references

Red Hat OpenShift AI product documentation informed the EvalHub REST API
usage in `examples/06_evalhub_native.ipynb`. API endpoints, payload shapes and
header names are interface facts; no documentation prose is reproduced here.

## Original content

The adversarial prompts in `packages/frontend/src/components/AttackDemo.tsx`
were written for this project. They exercise well-known injection techniques,
but the wording is original and stays in the restaurant domain. No third-party
jailbreak corpus is reproduced.

`examples/sekki_data.py` — seasonal descriptions and haiku written for this
project (LLM-assisted). Fictional demo content for a fictional restaurant; the
`health_wisdom` entries are not culinary or medical advice.

## Trademarks

TableSchnappi is a personal project. It is not affiliated with, endorsed by,
or supported by Red Hat, Inc., NVIDIA, Meta, IBM, Bandai, or any other company
whose products it integrates with or references.

Red Hat, OpenShift and Red Hat OpenShift AI are trademarks of Red Hat, Inc.
NeMo is a trademark of NVIDIA Corporation. Llama is a trademark of Meta
Platforms, Inc. Granite is a trademark of International Business Machines
Corporation. All other trademarks are the property of their respective owners
and are used nominatively, solely to identify the products this software
interoperates with.
