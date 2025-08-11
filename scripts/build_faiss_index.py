# scripts/build_faiss_index.py
import os
import json
import faiss
import numpy as np
from pathlib import Path
from openai import OpenAI
from utils.field_chunker import transaction_to_text
import argparse
import sys

# ---- Resolve project-rooted absolute paths ----
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH  = PROJECT_ROOT / "data" / "transactions.json"
INDEX_DIR  = PROJECT_ROOT / "data" / "index"
INDEX_PATH = INDEX_DIR / "transactions_faiss_index_flat.faiss"

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-en-icl")

def _embed(texts, verbose=False):
    base_url = os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE")
    api_key  = os.getenv("OPENAI_API_KEY")
    if not api_key or not base_url:
        raise RuntimeError(
            "Missing OpenAI config. Set OPENAI_API_KEY and OPENAI_BASE_URL (or OPENAI_API_BASE)."
        )

    if verbose:
        print(f"[embed] base_url={base_url}")
        print(f"[embed] model={EMBED_MODEL}")
        print(f"[embed] batching={len(texts)} items total")

    client = OpenAI(api_key=api_key, base_url=base_url)
    vecs = []
    for i in range(0, len(texts), 64):
        batch = texts[i:i+64]
        if verbose:
            print(f"[embed] batch {i}-{i+len(batch)-1}")
        resp = client.embeddings.create(model=EMBED_MODEL, input=batch)
        if not hasattr(resp, "data") or not resp.data:
            raise RuntimeError(f"Embeddings API returned no data for batch starting at {i}")
        vecs.extend([d.embedding for d in resp.data])

    V = np.array(vecs, dtype="float32")
    # normalize for cosine; use FlatIP index
    V /= (np.linalg.norm(V, axis=1, keepdims=True) + 1e-8)
    return V

def main(verbose=False):
    if verbose:
        print(f"[paths] PROJECT_ROOT={PROJECT_ROOT}")
        print(f"[paths] DATA_PATH={DATA_PATH}")
        print(f"[paths] INDEX_PATH={INDEX_PATH}")

    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Transactions not found: {DATA_PATH}")

    with DATA_PATH.open("r", encoding="utf-8") as f:
        txns = json.load(f)
    if verbose:
        print(f"[data] transactions={len(txns)}")

    texts = [transaction_to_text(t) for t in txns]
    V = _embed(texts, verbose=verbose)

    dim = V.shape[1]
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    index = faiss.IndexFlatIP(dim)  # cosine on normalized vectors
    index.add(V)
    faiss.write_index(index, str(INDEX_PATH))

    if verbose:
        print(f"[ok] vectors={len(txns)}, dim={dim}")
        print(f"[ok] wrote index → {INDEX_PATH}")
    else:
        print(f"✅ Built FAISS index: {INDEX_PATH} (n={len(txns)}, dim={dim})")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    try:
        main(verbose=args.verbose)
    except Exception as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)