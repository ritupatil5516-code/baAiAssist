
import os, json, faiss, numpy as np, subprocess
from openai import OpenAI
from scripts.query_rewriter import rewrite_query
from utils.field_chunker import transaction_to_text
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH   = PROJECT_ROOT / "data" / "index" / "transactions_faiss_index_flat.faiss"
DATA_PATH    = PROJECT_ROOT / "data" / "transactions.json"
GLOSSARY_PATH= PROJECT_ROOT / "data" / "domain_glossary.yaml"

CHAT_MODEL  = os.getenv("CHAT_MODEL",  "meta-llama/Llama-3.3-70B-Instruct")
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-en-icl")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("OPENAI_API_BASE"))

def _ensure_index():
    if os.path.exists(INDEX_PATH):
        return
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    print("FAISS index not found. Building via scripts/build_faiss_index.py ...")
    subprocess.check_call(["python", "scripts/build_faiss_index.py"])

def _embed(texts: list[str]) -> np.ndarray:
    vecs = []
    for i in range(0, len(texts), 64):
        resp = client.embeddings.create(model=EMBED_MODEL, input=texts[i:i+64])
        vecs.extend([d.embedding for d in resp.data])
    V = np.array(vecs, dtype="float32")
    V /= (np.linalg.norm(V, axis=1, keepdims=True) + 1e-8)
    return V

class BankingCopilotAgent:
    def __init__(self, top_k: int = 8):
        _ensure_index()
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(DATA_PATH)
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            self.transactions = json.load(f)
        self.index = faiss.read_index(INDEX_PATH)
        self.top_k = top_k
        if os.path.exists(GLOSSARY_PATH):
            with open(GLOSSARY_PATH, "r", encoding="utf-8") as f:
                self.glossary = f.read()
        else:
            self.glossary = ""

    def search(self, user_query: str):
        rewritten = rewrite_query(user_query)
        qv = _embed([rewritten])
        sims, idxs = self.index.search(qv, self.top_k)
        hits = [self.transactions[i] for i in idxs[0] if i != -1]
        return hits, rewritten

    def answer(self, user_query: str) -> str:
        results, rewritten = self.search(user_query)
        context = "\n".join(transaction_to_text(t) for t in results)
        system_prompt = (
            "You are a banking assistant. Answer ONLY using the provided transactions and glossary. "
            "If the data is insufficient, say: 'Information not available in the provided data.'"
        )
        user_prompt = (
            f"Glossary:\n{self.glossary}\n\n"
            f"Retrieved transactions (top {self.top_k}):\n{context}\n\n"
            f"Original question: {user_query}\n"
            f"Rewritten for retrieval: {rewritten}\n\n"
            "Return a concise answer in natural language."
        )
        resp = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0
        )
        return resp.choices[0].message["content"].strip()
