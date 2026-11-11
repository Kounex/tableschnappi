"""
Docling-based sekki PDF ingestion pipeline → LlamaStack Milvus vector store.

Run ONCE after generating PDFs:
  python3 examples/sekki_ingest.py

Requires:
  pip install docling mlflow[kubernetes] httpx

What it does:
  1. Converts each sekki PDF to structured markdown via Docling
  2. Chunks by semantic section (preserving sekki structure)
  3. Upserts into a LlamaStack vector store (Milvus backend)
  4. Logs ingestion metrics to MLflow for observability

The vector store ID is printed at the end — set it as
SEKKI_VECTOR_STORE_ID in the mlflow-proxy deployment.
"""
import os, sys, json, time, hashlib
from pathlib import Path
from datetime import datetime

import httpx
import mlflow

# ── Config ─────────────────────────────────────────────────────────────────────
LLAMASTACK_BASE = os.environ.get(
    "LLAMASTACK_BASE",
    "",  # no default: a real-looking one dials a namespace you do not own
)

# Optional: a docling-serve endpoint, which is far lighter than installing
# Docling here. Behind a LiteLLM/MaaS gateway the route is a passthrough —
# /docling/<docling-serve-path> — and the body must still carry "model", even
# though it is not a chat model. Chat-completions against it 404s.
#   DOCLING_URL=https://<gateway>        DOCLING_KEY=sk-...
# With these set, no local Docling install or model download is needed.
DOCLING_URL   = os.environ.get("DOCLING_URL", "").rstrip("/")
DOCLING_KEY   = os.environ.get("DOCLING_KEY", "")
DOCLING_MODEL = os.environ.get("DOCLING_MODEL", "Docling")
# Set MLFLOW_TRACKING_URI for your cluster (e.g. https://rh-ai.apps.<CLUSTER_DOMAIN>/mlflow)
MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI", "")
PDF_DIR = Path(__file__).parent / "sekki_pdfs"
VECTOR_STORE_NAME = "sakura-sekki-knowledge"
EMBEDDING_MODEL   = "ibm-granite/granite-embedding-125m-english"

# ── Setup MLflow ───────────────────────────────────────────────────────────────
os.environ["MLFLOW_TRACKING_AUTH"]         = "kubernetes-namespaced"
os.environ["MLFLOW_K8S_INTEGRATION"]       = "true"
os.environ["MLFLOW_TRACKING_INSECURE_TLS"] = "true"
mlflow.set_tracking_uri(MLFLOW_URI)
mlflow.set_experiment("restaurant-chatbot-traces")


def ls_get(path: str) -> dict:
    r = httpx.get(f"{LLAMASTACK_BASE}{path}", timeout=30)
    r.raise_for_status()
    return r.json()


def ls_post(path: str, body: dict) -> dict:
    r = httpx.post(f"{LLAMASTACK_BASE}{path}", json=body, timeout=60)
    r.raise_for_status()
    return r.json()


# ── Step 1: Docling PDF → markdown ────────────────────────────────────────────
def _convert_remote(pdf_path: Path) -> str:
    """Convert one PDF to markdown via a docling-serve endpoint."""
    import base64, re
    payload = {
        # Required even on the passthrough route: the gateway needs it to
        # pick a deployment. Omitting it returns {"detail": "'model' is required"}.
        "model": DOCLING_MODEL,
        "options": {"to_formats": ["md"], "do_ocr": False},
        "sources": [{
            "kind": "file",
            "base64_string": base64.b64encode(pdf_path.read_bytes()).decode(),
            "filename": pdf_path.name,
        }],
    }
    headers = {"Authorization": f"Bearer {DOCLING_KEY}"} if DOCLING_KEY else {}
    r = httpx.post(f"{DOCLING_URL}/docling/v1/convert/source",
                   json=payload, headers=headers, timeout=300)
    r.raise_for_status()
    md = (r.json().get("document") or {}).get("md_content") or ""
    # Docling embeds page images as base64 data URIs. On these PDFs that is
    # ~85% of the payload and none of it is retrievable text.
    return re.sub(r"!\[Image\]\(data:image/[^)]+\)", "", md).strip()


def convert_pdfs(pdf_dir: Path) -> list[dict]:
    """Convert all PDFs to structured text chunks.

    Three paths, in order of preference: a remote docling-serve endpoint
    (nothing to install), a local Docling install, or a plain-text fallback
    that reads sekki_data.py directly.
    """
    if DOCLING_URL:
        print(f"Using the Docling endpoint at {DOCLING_URL}")
        pdfs = sorted(pdf_dir.glob("*.pdf"))
        if not pdfs:
            sys.exit(f"No PDFs found in {pdf_dir}. Run generate_sekki_pdfs.py first.")
        out = []
        for pdf_path in pdfs:
            md = _convert_remote(pdf_path)
            if len(md) < 200:
                print(f"  [WARN] {pdf_path.name}: only {len(md)} chars, skipping")
                continue
            print(f"  {pdf_path.name}: {len(md)} chars")
            # One chunk per sekki. These documents are ~3.5k characters, well
            # inside the embedding window, and the sekki is the unit a guest
            # actually asks about — splitting it separates a dish from the
            # season that justifies it.
            out.append({
                "id":       f"{pdf_path.stem}__chunk_000",
                "text":     md,
                "sekki_id": pdf_path.stem,
                "source":   pdf_path.name,
                "chunk":    0,
            })
        return out

    try:
        from docling.document_converter import DocumentConverter
        from docling.chunking import HybridChunker
        from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
        from transformers import AutoTokenizer
        converter = DocumentConverter()
        # Chunker tokenizer must match the embedding model's tokenizer so
        # token-count estimates during chunking are accurate (Docling's own
        # guidance) — use the same granite-embedding model as EMBEDDING_MODEL.
        tokenizer = HuggingFaceTokenizer(
            tokenizer=AutoTokenizer.from_pretrained(EMBEDDING_MODEL),
            max_tokens=400,
        )
        chunker = HybridChunker(tokenizer=tokenizer, merge_peers=True)
        use_docling = True
    except ImportError:
        print("  [WARN] docling not installed — using plain text extraction fallback")
        use_docling = False

    pdfs = sorted(pdf_dir.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found in {pdf_dir}. Run generate_sekki_pdfs.py first.")

    print(f"Converting {len(pdfs)} PDFs...")
    all_chunks = []

    for pdf_path in pdfs:
        sekki_id = pdf_path.stem  # e.g. "01_shokan"
        print(f"  Processing {pdf_path.name}")

        if use_docling:
            result = converter.convert(str(pdf_path))
            doc    = result.document
            chunks = list(chunker.chunk(doc))
            for i, chunk in enumerate(chunks):
                text = chunk.text.strip()
                if len(text) < 20:
                    continue
                all_chunks.append({
                    "id":       f"{sekki_id}__chunk_{i:03d}",
                    "text":     text,
                    "sekki_id": sekki_id,
                    "source":   pdf_path.name,
                    "chunk":    i,
                })
        else:
            # Fallback: read the sekki data directly from sekki_data.py
            sys.path.insert(0, str(Path(__file__).parent))
            from sekki_data import SEKKI
            number = int(sekki_id.split("_")[0])
            s = next((x for x in SEKKI if x["number"] == number), None)
            if s:
                text = _sekki_to_text(s)
                all_chunks.append({
                    "id":       f"{sekki_id}__chunk_000",
                    "text":     text,
                    "sekki_id": sekki_id,
                    "source":   pdf_path.name,
                    "chunk":    0,
                })

    print(f"  → {len(all_chunks)} chunks total")
    return all_chunks


def _sekki_to_text(s: dict) -> str:
    """Serialize sekki dict to plain text for fallback ingestion."""
    lines = [
        f"{s['kanji']} ({s['romaji']}) — {s['english']}",
        f"Period: approx. month {s['start_month']} day {s['start_day']}",
        "",
        s["description"],
        "",
        "Signs in nature: " + "; ".join(s["nature_signs"]),
        "",
        "Shun ingredients (peak season): " + ", ".join(
            f"{i['name_en']} ({i['name_ja']})" for i in s["shun_ingredients"]
        ),
        "",
        "Traditional wisdom: " + s["health_wisdom"],
        "",
        "At Sakura Restaurant: " + " | ".join(s["sakura_recommendations"]),
    ]
    return "\n".join(lines)


# ── Step 2: Create / retrieve vector store ────────────────────────────────────
def get_or_create_vector_store() -> str:
    """Return the ID of the sekki vector store, creating it if needed."""
    existing = ls_get("/v1/vector_stores?limit=100")
    for vs in existing.get("data", []):
        if vs.get("name") == VECTOR_STORE_NAME:
            print(f"  Vector store already exists: {vs['id']}")
            return vs["id"]

    resp = ls_post("/v1/vector_stores", {
        "name":             VECTOR_STORE_NAME,
        "embedding_model":  EMBEDDING_MODEL,
        "embedding_dimension": 768,  # granite-embedding-125m-english output size
    })
    vs_id = resp["id"]
    print(f"  Created vector store: {vs_id}")
    return vs_id


# ── Step 3: Ingest chunks ─────────────────────────────────────────────────────
def ingest_chunks(vs_id: str, chunks: list[dict]) -> int:
    """Upload text chunks to the LlamaStack vector store."""
    inserted = 0

    # Check what's already in the store (idempotent re-runs)
    try:
        existing = ls_get(f"/v1/vector_stores/{vs_id}/files?limit=200")
        existing_ids = {f["id"] for f in existing.get("data", [])}
    except Exception:
        existing_ids = set()

    for chunk in chunks:
        chunk_id = chunk["id"]
        if chunk_id in existing_ids:
            continue  # skip already-ingested chunks

        # Upload as a file
        file_resp = ls_post("/v1/files", {
            "purpose": "assistants",
            "file":    chunk["text"],
            "filename": f"{chunk_id}.txt",
        })
        file_id = file_resp.get("id", "")

        # Add to vector store
        ls_post(f"/v1/vector_stores/{vs_id}/files", {
            "file_id": file_id,
        })
        inserted += 1

    return inserted


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=== Sekki Knowledge Ingestion Pipeline ===\n")
    start = time.time()

    with mlflow.start_run(run_name="sekki-ingestion"):
        # Step 1: Convert PDFs
        chunks = convert_pdfs(PDF_DIR)
        mlflow.log_metric("chunks_extracted", len(chunks))

        # Step 2: Vector store
        print("\nPreparing vector store...")
        vs_id = get_or_create_vector_store()
        mlflow.log_param("vector_store_id",   vs_id)
        mlflow.log_param("vector_store_name", VECTOR_STORE_NAME)
        mlflow.log_param("embedding_model",   EMBEDDING_MODEL)

        # Step 3: Ingest
        print(f"\nIngesting {len(chunks)} chunks into {vs_id}...")
        inserted = ingest_chunks(vs_id, chunks)
        elapsed = round(time.time() - start, 1)

        mlflow.log_metrics({
            "chunks_inserted":  inserted,
            "chunks_skipped":   len(chunks) - inserted,
            "elapsed_seconds":  elapsed,
        })

        print(f"\n{'='*40}")
        print(f"Inserted:  {inserted} new chunks")
        print(f"Skipped:   {len(chunks) - inserted} (already in store)")
        print(f"Elapsed:   {elapsed}s")
        print(f"\nVector store ID: {vs_id}")
        print("\nSet this in your deployment:")
        print(f"  SEKKI_VECTOR_STORE_ID={vs_id}")
        print("\nLogged to MLflow.")


if __name__ == "__main__":
    main()
