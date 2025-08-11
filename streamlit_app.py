
import streamlit as st
from scripts.agent import BankingCopilotAgent

st.set_page_config(page_title="Banking Copilot v2.0.0", layout="wide")
st.title("🏦 Banking Copilot v2.0.0")

if "agent" not in st.session_state:
    st.session_state.agent = BankingCopilotAgent()

if "history" not in st.session_state:
    st.session_state.history = []

q = st.text_input("Ask a question about your transactions…", key="query")
col1, col2 = st.columns([1,1])
with col1:
    if st.button("Ask"):
        if q.strip():
            ans = st.session_state.agent.answer(q.strip())
            st.session_state.history.append({"q": q.strip(), "a": ans})
with col2:
    if st.button("Rebuild FAISS index"):
        import subprocess
        try:
            subprocess.check_call(["python", "scripts/build_faiss_index.py"])
            st.success("FAISS index rebuilt ✅")
        except Exception as e:
            st.error(f"Build failed: {e}")

st.divider()
for chat in reversed(st.session_state.history):
    st.markdown(f"**You:** {chat['q']}")
    st.markdown(f"**Copilot:** {chat['a']}")
