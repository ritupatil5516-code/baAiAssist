import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from scripts.query_rewriter import rewrite_query
from utils.field_chunker import transaction_to_text

DATA_PATH = "data/transactions.json"
INDEX_PATH = "data/index/transactions_faiss_index_flat.faiss"
GLOSSARY_PATH = "data/domain_glossary.yaml"
EMBED_MODEL = "BAAI/bge-small-en"

class BankingCopilotAgent:
    def __init__(self):
        self.model = SentenceTransformer(EMBED_MODEL)
        self.index = faiss.read_index(INDEX_PATH)
        with open(DATA_PATH, "r") as f:
            self.transactions = json.load(f)
        with open(GLOSSARY_PATH, "r") as f:
            self.glossary = f.read()

    def search(self, query, top_k=5):
        query = rewrite_query(query)
        emb = self.model.encode([query], convert_to_numpy=True)
        D, I = self.index.search(emb, top_k)
        results = [self.transactions[i] for i in I[0] if i != -1]
        return results

    def answer(self, query):
        results = self.search(query)
        context = "\n".join(transaction_to_text(txn) for txn in results)
        prompt = f"Glossary:\n{self.glossary}\n\nTransactions:\n{context}\n\nQuestion: {query}\nAnswer:"
        # Here you would call your LLaMA/OpenAI model, e.g.:
        # return llama_chat(prompt)
        return prompt  # For now, just returns prompt for testing