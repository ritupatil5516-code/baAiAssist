import streamlit as st
from scripts.agent import BankingCopilotAgent

st.set_page_config(page_title="Banking Copilot v2.0.0", layout="wide")
st.title("🏦 Banking Copilot v2.0.0")

agent = BankingCopilotAgent()

if "history" not in st.session_state:
    st.session_state.history = []

query = st.text_input("Ask a question about your transactions:")
if st.button("Ask") and query:
    answer = agent.answer(query)
    st.session_state.history.append({"query": query, "answer": answer})

for chat in reversed(st.session_state.history):
    st.markdown(f"**You:** {chat['query']}")
    st.markdown(f"**Copilot:** {chat['answer']}")