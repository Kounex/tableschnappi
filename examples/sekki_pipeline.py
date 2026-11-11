"""
Sekki Knowledge Ingestion -- Kubeflow Pipeline (KFP v2)
Follows opendatahub-io/data-processing patterns exactly.

REPO_URL is public, so stage 1 clones it anonymously and no credentials are
needed. If you fork into a private repository, set GITHUB_TOKEN on the
clone step yourself.

Run from a RHOAI workbench to compile and submit:

  pip install kfp==2.14.6        # add kfp-kubernetes only if you fork privately
  python3 examples/sekki_pipeline.py                     # compile only -> sekki_pipeline.yaml
  python3 examples/sekki_pipeline.py --submit             # compile + submit a one-off run
  python3 examples/sekki_pipeline.py --submit-recurring   # compile + create a weekly recurring run
                                                           # (default: every Sunday 03:00 -- override
                                                           # with --cron="<expr>")

Pipeline stages:
  1. clone_repo      -- git clone tableschnappi from GitHub
  2. generate_pdfs   -- fpdf2: produce 24 sekki PDFs
  3. download_models -- docling model artifacts (cached)
  4. convert_docling -- Docling PDF -> markdown + JSONL chunks
  5. ingest_milvus   -- LlamaStack vector_io: chunks -> Milvus
  6. verify_and_log  -- test query + MLflow metrics


Keep this file ASCII-only. The compiled spec is stored in the Data Science
Pipelines MariaDB, whose PipelineSpec column rejects multi-byte characters --
an arrow or a kanji anywhere in here fails the upload with
"Error 1366 (22007): Incorrect string value". The Japanese content is not
affected: it lives in the PDFs and chunks this pipeline produces, not in the
pipeline definition.
"""

import os
from kfp import dsl, compiler
from kfp import kubernetes

# -- Base images (matching opendatahub-io/data-processing) ---------------------
PYTHON_BASE_IMAGE  = os.getenv(
    "PYTHON_BASE_IMAGE",
    "registry.access.redhat.com/ubi9/python-311:9.6-1755074620",
)

# -- Defaults -------------------------------------------------------------------
REPO_URL      = "https://github.com/KiriGould/tableschnappi"
LLAMASTACK    = os.environ.get("LLAMASTACK_BASE", "")
# Set MLFLOW_URI for your cluster (e.g. https://rh-ai.apps.<CLUSTER_DOMAIN>/mlflow)
MLFLOW_URI    = os.getenv("MLFLOW_URI", "")
MLFLOW_EXP    = "restaurant-chatbot-traces"
VS_NAME       = "sakura-sekki-knowledge"
# docling-serve, reached through the platform gateway. No default host: a
# real-looking one dials somebody else's cluster.
DOCLING_URL   = os.environ.get("DOCLING_URL", "")
DOCLING_MODEL = os.environ.get("DOCLING_MODEL", "Docling")
DOCLING_SECRET= os.environ.get("DOCLING_SECRET", "docling-gateway")
EMBED_MODEL   = "ibm-granite/granite-embedding-125m-english"


# -- Stage 1: Clone repo --------------------------------------------------------

@dsl.component(
    base_image=PYTHON_BASE_IMAGE,
    packages_to_install=["gitpython"],
)
def clone_repo(
    repo_url: str,
    repo_dir: dsl.Output[dsl.Artifact],
):
    import os
    import subprocess
    from pathlib import Path

    # Clone INTO the output artifact, not into /tmp. Each KFP step is its own
    # pod, so a local path handed to the next step points at nothing -- this
    # used to write /tmp/tableschnappi here and read it back in stage 2, which
    # failed with FileNotFoundError every time. Only the artifact crosses the
    # step boundary, so the files have to live inside it.
    out = Path(repo_dir.path)
    out.mkdir(parents=True, exist_ok=True)
    dest = str(out / "repo")

    # The repo is public, so this clones anonymously. If you fork privately,
    # set GITHUB_TOKEN on this step and the URL is rewritten to use it.
    token = os.environ.get("GITHUB_TOKEN", "")
    clone_url = repo_url
    if token and clone_url.startswith("https://"):
        clone_url = clone_url.replace("https://", f"https://{token}@", 1)

    subprocess.run(["git", "clone", "--depth=1", clone_url, dest], check=True)

    n = sum(1 for _ in Path(dest).rglob("*"))
    print(f"Cloned {repo_url} -> artifact ({n} entries)")  # never print clone_url


# -- Stage 2: Generate PDFs -----------------------------------------------------

@dsl.component(
    base_image=PYTHON_BASE_IMAGE,
    packages_to_install=["fpdf2>=2.7.9", "requests"],
)
def generate_pdfs(
    repo_dir: dsl.Input[dsl.Artifact],
    pdf_dir:  dsl.Output[dsl.Artifact],
):
    import subprocess, sys, os, urllib.request
    from pathlib import Path

    repo = Path(repo_dir.path) / "repo"
    # This fork keeps optional examples separate; upstream uses workshop/.
    scripts = repo / "examples"
    if not (scripts / "generate_sekki_pdfs.py").exists():
        scripts = repo / "workshop"
    sys.path.insert(0, str(scripts))

    out = Path(pdf_dir.path)
    out.mkdir(parents=True, exist_ok=True)

    # Download Noto Sans JP font (Unicode CJK support)
    font_path = "/tmp/NotoSansJP.ttf"
    if not Path(font_path).exists():
        print("Downloading NotoSansJP font...")
        urllib.request.urlretrieve(
            "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf",
            font_path,
        )

    env = {**os.environ, "SEKKI_PDF_OUT": str(out), "NOTO_FONT_PATH": font_path}
    result = subprocess.run(
        [sys.executable, str(scripts / "generate_sekki_pdfs.py")],
        cwd=repo, env=env, capture_output=True, text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:", result.stderr[-2000:])
        raise RuntimeError("PDF generation failed")

    pdfs = list(out.glob("*.pdf"))
    # Fail here rather than hand an empty artifact to the next stage. This
    # step used to report success on zero PDFs, so the real error surfaced
    # two stages later as "did stage 2 run?".
    if not pdfs:
        raise RuntimeError(
            f"generate_sekki_pdfs.py wrote nothing to {out}. It must honour "
            "SEKKI_PDF_OUT."
        )
    print(f"Generated {len(pdfs)} PDFs -> {out}")


# -- Stage 3: Convert PDFs via a docling-serve endpoint ------------------------

@dsl.component(
    base_image=PYTHON_BASE_IMAGE,
    packages_to_install=["httpx>=0.27"],
)
def convert_via_docling_serve(
    pdf_dir:        dsl.Input[dsl.Artifact],
    chunks_dir:     dsl.Output[dsl.Artifact],
    docling_url:    str,
    docling_model:  str = "Docling",
    min_chars:      int = 200,
):
    """Convert each PDF to markdown with a remote docling-serve.

    This replaces two earlier stages that pip-installed Docling and downloaded
    its layout and tableformer models into the pod. That cost several GB and
    minutes per run for a conversion the platform can already do, and on a
    busy node it filled ephemeral storage and got the pod evicted.

    The API key is read from DOCLING_KEY in the environment, not passed as a
    pipeline parameter -- parameters are visible in the run UI. Attach it with
    kfp.kubernetes.use_secret_as_env in the pipeline definition.
    """
    import base64, json, os, re
    from pathlib import Path
    import httpx

    key = os.environ.get("DOCLING_KEY", "")
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    base = docling_url.rstrip("/")

    out = Path(chunks_dir.path)
    out.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(Path(pdf_dir.path).glob("*.pdf"))
    if not pdfs:
        raise RuntimeError(f"No PDFs in {pdf_dir.path} -- did stage 2 run?")

    all_chunks, failed = [], []
    for pdf in pdfs:
        payload = {
            # Required even on the passthrough route: the gateway needs it to
            # choose a deployment. Without it: {"detail": "'model' is required"}.
            "model": docling_model,
            "options": {"to_formats": ["md"], "do_ocr": False},
            "sources": [{
                "kind": "file",
                "base64_string": base64.b64encode(pdf.read_bytes()).decode(),
                "filename": pdf.name,
            }],
        }
        r = httpx.post(f"{base}/docling/v1/convert/source",
                       json=payload, headers=headers, timeout=300)
        r.raise_for_status()
        md = (r.json().get("document") or {}).get("md_content") or ""
        # Docling embeds page images as base64 data URIs. On these documents
        # that is roughly 85% of the payload and none of it is retrievable.
        md = re.sub(r"!\[Image\]\(data:image/[^)]+\)", "", md).strip()
        if len(md) < min_chars:
            failed.append(pdf.name)
            print(f"  {pdf.name}: only {len(md)} chars, skipped")
            continue
        print(f"  {pdf.name}: {len(md)} chars")
        # One chunk per sekki. These are ~3.5k characters, inside the embedding
        # window, and the sekki is the unit a guest asks about -- splitting it
        # separates a dish from the season that justifies it.
        all_chunks.append({
            "id":       f"{pdf.stem}__chunk_000",
            "text":     md,
            "sekki_id": pdf.stem,
            "source":   pdf.name,
            "chunk":    0,
        })

    jsonl = out / "sekki_chunks.jsonl"
    with open(jsonl, "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    if not all_chunks:
        raise RuntimeError("Every PDF failed to convert -- check docling_url and DOCLING_KEY.")
    print(f"Converted {len(all_chunks)}/{len(pdfs)} -> {jsonl}")
    if failed:
        print("Skipped:", ", ".join(failed))


# -- Stage 5: Ingest into LlamaStack Milvus ------------------------------------

@dsl.component(
    base_image=PYTHON_BASE_IMAGE,
    packages_to_install=["httpx>=0.27"],
)
def ingest_to_vector_store(
    chunks_dir:          dsl.Input[dsl.Artifact],
    llamastack_base:     str,
    vector_store_name:   str,
    embedding_model:     str,
    vector_store_id_out: dsl.Output[dsl.Artifact],
):
    import json
    from pathlib import Path
    import httpx

    def get(path):
        r = httpx.get(f"{llamastack_base}{path}", timeout=30)
        r.raise_for_status()
        return r.json()

    def post(path, body):
        r = httpx.post(f"{llamastack_base}{path}", json=body, timeout=60)
        r.raise_for_status()
        return r.json()

    # Load chunks from JSONL
    chunks_path = Path(chunks_dir.path) / "sekki_chunks.jsonl"
    chunks = [json.loads(l) for l in chunks_path.read_text().splitlines() if l.strip()]
    print(f"Loaded {len(chunks)} chunks")

    # Get or create vector store (idempotent)
    existing = get("/v1/vector_stores?limit=100").get("data", [])
    vs = next((s for s in existing if s.get("name") == vector_store_name), None)
    if vs:
        vs_id = vs["id"]
        print(f"Using existing vector store: {vs_id}")
    else:
        # Resolve the embedding model against what this LlamaStack actually
        # serves. Providers prefix their identifiers -- the granite embedder
        # is registered as "sentence-transformers/ibm-granite/..." -- so the
        # bare name is rejected with "Model not found" and the whole stage
        # dies on a 400.
        wanted = embedding_model
        try:
            served = [m.get("identifier") or m.get("id") for m in
                      (get("/v1/models").get("data") or get("/v1/models"))]
            served = [m for m in served if m]
            match = next((m for m in served if m == wanted), None) \
                 or next((m for m in served if m.endswith("/" + wanted)), None) \
                 or next((m for m in served if wanted in m), None)
            if match and match != wanted:
                print(f"Resolved embedding model {wanted} -> {match}")
                wanted = match
            elif not match:
                print(f"WARNING: {wanted} is not in this LlamaStack's model list; "
                      f"trying it anyway. Available: {served}")
        except Exception as e:
            print("Could not list models, using the name as given:", e)

        vs_id = post("/v1/vector_stores", {
            "name":                vector_store_name,
            "embedding_model":     wanted,
            "embedding_dimension": 768,  # granite-embedding-125m-english output size
        })["id"]
        print(f"Created vector store: {vs_id}")

    # Skip chunks already in this store, so a re-run is idempotent.
    #
    # This used to collect LlamaStack file ids (file-xxxx) and compare them
    # with chunk ids (01_shokan__chunk_000). They never matched, so nothing
    # was ever skipped and every re-run added another full copy of all 24
    # documents. Match on filename instead, which is what carries the chunk
    # id across the two APIs.
    existing_names = set()
    try:
        store_file_ids = [f["id"] for f in
                          get(f"/v1/vector_stores/{vs_id}/files?limit=500").get("data", [])]
        by_id = {f["id"]: f.get("filename", "") for f in
                 get("/v1/files?limit=1000").get("data", [])}
        existing_names = {by_id.get(i, "") for i in store_file_ids} - {""}
        print(f"Store already holds {len(existing_names)} document(s)")
    except Exception as e:
        print("Could not list existing files, will insert everything:", e)

    inserted = 0
    for chunk in chunks:
        if f"{chunk['id']}.md" in existing_names:
            continue
        # /v1/files is multipart/form-data, not JSON. Posting JSON here
        # returned a bare 400 with no hint about the content type.
        fr = httpx.post(
            f"{llamastack_base}/v1/files",
            data={"purpose": "assistants"},
            files={"file": (f"{chunk['id']}.md", chunk["text"].encode("utf-8"),
                            "text/markdown")},
            timeout=120,
        )
        fr.raise_for_status()
        file_id = fr.json()["id"]
        # Attaching chunks the store: LlamaStack does the embedding.
        post(f"/v1/vector_stores/{vs_id}/files", {"file_id": file_id})
        inserted += 1

    print(f"Inserted {inserted} new chunks ({len(chunks) - inserted} skipped)")

    out = Path(vector_store_id_out.path)
    out.mkdir(parents=True, exist_ok=True)
    (out / "vs_id.txt").write_text(vs_id)


# -- Stage 6: Verify + log to MLflow -------------------------------------------

@dsl.component(
    base_image=PYTHON_BASE_IMAGE,
    packages_to_install=["httpx>=0.27", "mlflow[kubernetes]>=3.11"],
)
def verify_and_log(
    chunks_dir:          dsl.Input[dsl.Artifact],
    vector_store_id_out: dsl.Input[dsl.Artifact],
    llamastack_base:     str,
    mlflow_uri:          str,
    mlflow_experiment:   str,
    mlflow_secret_path:  str = "/mnt/secrets",
):
    import json, os
    from pathlib import Path
    import httpx, mlflow

    vs_id  = (Path(vector_store_id_out.path) / "vs_id.txt").read_text().strip()
    chunks = [(Path(chunks_dir.path) / "sekki_chunks.jsonl").read_text().splitlines()]
    total  = len([l for l in chunks[0] if l.strip()])

    # Test query -- should return seasonal food knowledge
    r = httpx.post(
        f"{llamastack_base}/v1/vector_stores/{vs_id}/search",
        json={"query": "Major Heat eel unagi summer", "max_results": 3},
        timeout=15,
    )
    results = r.json().get("data", []) if r.status_code == 200 else []
    print(f"Test query returned {len(results)} results")
    if results:
        print(f"  Top hit: {results[0].get('content','')[:120]}")

    # MLflow logging
    os.environ["MLFLOW_TRACKING_AUTH"]         = "kubernetes-namespaced"
    os.environ["MLFLOW_K8S_INTEGRATION"]       = "true"
    os.environ["MLFLOW_TRACKING_INSECURE_TLS"] = "true"
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment(mlflow_experiment)

    with mlflow.start_run(run_name="sekki-ingestion-pipeline"):
        mlflow.log_metrics({
            "chunks_total":       total,
            "query_results":      len(results),
            "vector_store_ready": 1 if results else 0,
        })
        mlflow.log_params({
            "vector_store_id":   vs_id,
            "source":            "KiriGould/tableschnappi",
            "pipeline_type":     "kubeflow-kfp-v2",
            "embedding_model":   "granite-embedding-125m-english",
        })

    print(f"\n{'='*50}")
    print(f"Vector store ID: {vs_id}")
    print(f"Set SEKKI_VECTOR_STORE_ID={vs_id} in the mlflow-proxy deployment")
    print("Logged to MLflow OK")


# -- Pipeline -------------------------------------------------------------------

@dsl.pipeline(
    name="sekki-knowledge-ingestion",
    description=(
        "One-time ingestion of 24 Japanese sekki (sekki) seasonal PDFs into "
        "LlamaStack Milvus via Docling. Enables seasonal RAG in the Sakura AI assistant."
    ),
)
def sekki_ingestion_pipeline(
    repo_url:           str = REPO_URL,
    llamastack_base:    str = LLAMASTACK,
    vector_store_name:  str = VS_NAME,
    embedding_model:    str = EMBED_MODEL,
    mlflow_uri:         str = MLFLOW_URI,
    mlflow_experiment:  str = MLFLOW_EXP,
    docling_url:        str = DOCLING_URL,
    docling_model:      str = DOCLING_MODEL,
    # Name of a Secret in the run namespace holding the gateway token under
    # the key "token". Empty means an unauthenticated docling-serve.
    docling_secret:     str = DOCLING_SECRET,
):
    # Stage 1 -- public repo, cloned anonymously. If you fork privately, attach
    # your own Secret here with kfp.kubernetes.use_secret_as_env, mapping it to
    # GITHUB_TOKEN.
    clone = clone_repo(repo_url=repo_url)
    clone.set_caching_options(False)

    # Stage 2
    pdfs = generate_pdfs(repo_dir=clone.outputs["repo_dir"])
    pdfs.set_caching_options(False)
    pdfs.set_memory_request("512M").set_memory_limit("1G")
    pdfs.set_cpu_request("250m").set_cpu_limit("1")

    # Stage 3 -- conversion through the platform's Docling endpoint.
    chunks = convert_via_docling_serve(
        pdf_dir=pdfs.outputs["pdf_dir"],
        docling_url=docling_url,
        docling_model=docling_model,
    )
    chunks.set_caching_options(False)
    chunks.set_memory_request("512M").set_memory_limit("1G")
    chunks.set_cpu_request("250m").set_cpu_limit("1")
    if docling_secret:
        kubernetes.use_secret_as_env(
            chunks,
            secret_name=docling_secret,
            secret_key_to_env={"token": "DOCLING_KEY"},
        )

    # Stage 4
    ingest = ingest_to_vector_store(
        chunks_dir=chunks.outputs["chunks_dir"],
        llamastack_base=llamastack_base,
        vector_store_name=vector_store_name,
        embedding_model=embedding_model,
    )
    ingest.set_caching_options(False)

    # Stage 5
    verify = verify_and_log(
        chunks_dir=chunks.outputs["chunks_dir"],
        vector_store_id_out=ingest.outputs["vector_store_id_out"],
        llamastack_base=llamastack_base,
        mlflow_uri=mlflow_uri,
        mlflow_experiment=mlflow_experiment,
    )
    verify.set_caching_options(False)


# -- Compile + optional submit --------------------------------------------------

if __name__ == "__main__":
    import sys

    os.makedirs("pipelines_gen", exist_ok=True)
    out_yaml = "pipelines_gen/sekki_pipeline.yaml"
    compiler.Compiler().compile(sekki_ingestion_pipeline, out_yaml)
    print(f"Compiled -> {out_yaml}")
    print("Upload this YAML in: RHOAI Dashboard -> Data Science Pipelines -> Import pipeline")

    if "--submit" in sys.argv or "--submit-recurring" in sys.argv:
        import kfp
        client = kfp.Client()

        if "--submit-recurring" in sys.argv:
            cron = next(
                (a.split("=", 1)[1] for a in sys.argv if a.startswith("--cron=")),
                "0 3 * * 0",  # every Sunday 03:00
            )
            job = client.create_recurring_run(
                experiment_id=client.create_experiment("tableschnappi-ingestion").experiment_id,
                job_name="sekki-ingestion-weekly",
                pipeline_package_path=out_yaml,
                cron_expression=cron,
                enable_caching=True,
            )
            print(f"Created recurring run: {job.recurring_run_id} (cron: {cron})")
        else:
            run = client.create_run_from_pipeline_package(
                out_yaml,
                run_name="sekki-ingestion-run",
                enable_caching=True,
            )
            print(f"Submitted run: {run.run_id}")
