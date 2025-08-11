# 🏦 Banking Copilot v2.0.0 (FAISS Flat, OpenAI-Compatible)

- FAISS Flat (exact cosine) retrieval
- OpenAI-compatible embeddings: `BAAI/bge-en-icl`
- LLM via `CHAT_MODEL` (e.g., `meta-llama/Llama-3.3-70B-Instruct`)
- Field-aware chunking, query rewriting, glossary injection
- Streamlit chat UI + auto-build index when missing

## Quickstart
```bash
pip install -r requirements.txt

export OPENAI_BASE_URL="http://localhost:8000/v1"
export OPENAI_API_KEY="your_key"
export CHAT_MODEL="meta-llama/Llama-3.3-70B-Instruct"
export EMBED_MODEL="BAAI/bge-en-icl"

# (optional) generate new dataset
python scripts/generate_dataset.py

# build index (the app will auto-build if missing)
python scripts/build_faiss_index.py

streamlit run streamlit_app.py
```
