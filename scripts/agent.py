# scripts/agent.py (only the important bits)
from pathlib import Path
import os, json, faiss, numpy as np
from openai import OpenAI
from scripts.query_rewriter import rewrite_query
from utils.field_chunker import transaction_to_text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH     = PROJECT_ROOT / "data" / "transactions.json"
INDEX_PATH    = PROJECT_ROOT / "data" / "index" / "transactions_faiss_index_flat.faiss"
GLOSSARY_PATH = PROJECT_ROOT / "data" / "domain_glossary.yaml"

CHAT_MODEL  = os.getenv("CHAT_MODEL",  "meta-llama/Llama-3.3-70B-Instruct")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-en-icl")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE"))

def _embed_query(text: str) -> np.ndarray:
    e = client.embeddings.create(model=EMBED_MODEL, input=[text]).data[0].embedding
    v = np.asarray(e, dtype="float32")
    v /= (np.linalg.norm(v) + 1e-8)  # normalize for cosine/IP
    return v.reshape(1, -1)

class BankingCopilotAgent:
    def __init__(self, top_k: int = 8):
        if not INDEX_PATH.exists():
            raise FileNotFoundError(f"Index missing, build it: {INDEX_PATH}")
        self.index = faiss.read_index(str(INDEX_PATH))

        with DATA_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
            self.transactions = data if isinstance(data, list) else data.get("transactions", [])

        self.glossary = GLOSSARY_PATH.read_text(encoding="utf-8") if GLOSSARY_PATH.exists() else ""
        self.top_k = top_k

    def search(self, user_query: str):
        rewritten = rewrite_query(user_query)
        qv = _embed_query(rewritten)
        sims, idxs = self.index.search(qv, self.top_k)
        hits = [self.transactions[i] for i in idxs[0] if i != -1]
        return hits, rewritten

    def answer(self, user_query: str) -> str:
        results, rewritten = self.search(user_query)
        context = "\n".join(transaction_to_text(t) for t in results)
        sys = ("You are a banking assistant. Answer ONLY from the provided transactions and glossary. "
               "If insufficient, say 'Information not available in the provided data.'")
        user = (
            f"Glossary:\n{self.glossary}\n\n"
            f"Transactions (top {self.top_k}):\n{context}\n\n"
            f"Original question: {user_query}\n"
            f"Rewritten for retrieval: {rewritten}\n\n"
            "Return a concise answer."
        )
        resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role":"system","content":sys},{"role":"user","content":user}],
            temperature=0
        )
        return resp.choices[0].message["content"].strip()