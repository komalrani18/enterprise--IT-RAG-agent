"""
Streamlit chat interface for the Enterprise IT Support Agentic RAG backend.
"""
import os
import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="IT Support Assistant", page_icon="🛠️", layout="centered")

st.title("🛠️ Enterprise IT Support Assistant")
st.caption(
    "Ask about IT/HR policy — remote work, VPN, passwords, software installs, hardware "
    "requests. If it's not in our knowledge base, I'll search the web or open a ticket."
)

SOURCE_LABELS = {
    "knowledge_base": "📚 Answered from internal policy knowledge base",
    "web_search": "🌐 Answered from web search (not internal policy)",
    "ticket": "🎫 Escalated — IT ticket created",
}

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Backend status")
    try:
        health = requests.get(f"{BACKEND_URL}/health", timeout=5).json()
        st.success(f"Connected — {health.get('kb_chunks_indexed', 0)} policy chunks indexed")
    except Exception:
        st.error(f"Cannot reach backend at {BACKEND_URL}")

    st.subheader("Recent tickets")
    try:
        tickets = requests.get(f"{BACKEND_URL}/tickets", timeout=5).json().get("tickets", [])
        if tickets:
            for t in reversed(tickets[-5:]):
                st.markdown(f"**{t['id']}** — {t['question'][:60]}")
        else:
            st.caption("No tickets filed yet.")
    except Exception:
        st.caption("Ticket list unavailable.")

    if st.button("🔄 Re-run ingestion"):
        with st.spinner("Re-ingesting policy documents..."):
            try:
                resp = requests.post(f"{BACKEND_URL}/ingest", timeout=120).json()
                st.success(f"Ingested {resp.get('chunks_ingested', 0)} chunks.")
            except Exception as e:
                st.error(f"Ingestion failed: {e}")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("badge"):
            st.caption(msg["badge"])

if prompt := st.chat_input("Ask an IT/HR policy question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Routing your question through the agent..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/chat",
                    json={"question": prompt, "requester": "streamlit_user"},
                    timeout=90,
                )
                resp.raise_for_status()
                data = resp.json()
                answer = data["answer"]
                badge = SOURCE_LABELS.get(data["source"], data["source"])
                badge += f"  ·  KB hits: {data['kb_hits']}  ·  Web hits: {data['web_hits']}"
                if data.get("ticket_id"):
                    badge += f"  ·  Ticket: {data['ticket_id']}"
            except Exception as e:
                answer = f"Sorry, I couldn't reach the backend: {e}"
                badge = ""

            st.markdown(answer)
            if badge:
                st.caption(badge)

    st.session_state.messages.append({"role": "assistant", "content": answer, "badge": badge})
