import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from utils.field_chunker import transaction_to_text

DATA_PATH = "data/transactions.json"
INDEX_PATH = "data/index/transactions_faiss_index_flat.faiss"
EMBED_MODEL = "BAAI/bge-small-en"  # BGE small for efficiency

def build_faiss_index():
    with open(DATA_PATH, "r") as f:
        transactions = json.load(f)

    model = SentenceTransformer(EMBED_MODEL)
    texts = [transaction_to_text(txn) for txn in transactions]
    embeddings = model.encode(texts, convert_to_numpy=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    print(f"✅ FAISS index saved to {INDEX_PATH} with {len(transactions)} records.")

if __name__ == "__main__":
    build_faiss_index()