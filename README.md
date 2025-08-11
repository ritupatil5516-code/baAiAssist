# 🏦 Banking Copilot v2.0.0

A production-ready **banking AI copilot** that answers questions about transactions using **context engineering + FAISS semantic search** — no GPU fine-tuning required.

---

## 🚀 Features
- **Synthetic dataset** (~200 realistic transactions)
- **Domain glossary injection** for better banking-specific answers
- **FAISS Flat vector search** with field-aware chunking
- **Query rewriting** for date ranges and amounts
- **Calculation tool** for aggregations (e.g., total spend)
- **Multi-step reasoning agent**
- **Streamlit chat UI** with session history
- **Prebuilt FAISS index** for instant startup

---

## 📂 Project Structure

banking_copilot_v2.0.0/
├── README.md
├── requirements.txt
├── streamlit_app.py
├── data/
│   ├── transactions.json
│   ├── domain_glossary.yaml
│   └── index/
│       └── transactions_faiss_index_flat.faiss
├── scripts/
│   ├── generate_dataset.py
│   ├── build_faiss_index.py
│   ├── query_rewriter.py
│   ├── calc_tool.py
│   └── agent.py
└── utils/
└── field_chunker.py

---

## 🛠️ Setup & Run

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt

---

## 🛠️ Setup & Run

### 1️⃣ Install dependencies
```bash
pip install -r requirements.txt


streamlit run streamlit_app.py


