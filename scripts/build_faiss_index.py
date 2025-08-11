# scripts/build_faiss_index.py
import os, json, faiss, numpy as np
from pathlib import Path
from openai import OpenAI
from utils.field_chunker import transaction_to_text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH  = PROJECT_ROOT / "data" / "transactions.json"
INDEX_DIR  = PROJECT_ROOT / "data" / "index"
INDEX_PATH = INDEX_DIR / "transactions_faiss_index_flat.faiss"

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-en-icl")

def _embed(texts):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE"),
    )
    vecs = []
    for i in range(0, len(texts), 64):
        resp = client.embeddings.create(model=EMBED_MODEL, input=texts[i:i+64])
        vecs.extend([d.embedding for d in resp.data])
    V = np.asarray(vecs, dtype="float32")
    # normalize -> cosine with IndexFlatIP
    V /= (np.linalg.norm(V, axis=1, keepdims=True) + 1e-8)
    return V

def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Transactions not found: {DATA_PATH}")

    with DATA_PATH.open("r", encoding="utf-8") as f:
        # Works with either a list or an object containing a "transactions" array
        data = json.load(f)
        txns = data if isinstance(data, list) else data.get("transactions", [])

    texts = [transaction_to_text(t) for t in txns]
    V = _embed(texts)
    dim = V.shape[1]
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    index = faiss.IndexFlatIP(dim)      # exact cosine
    index.add(V)
    faiss.write_index(index, str(INDEX_PATH))
    print(f"✅ FAISS index → {INDEX_PATH} (n={len(txns)}, dim={dim})")

if __name__ == "__main__":
    main()