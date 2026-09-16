"""
FastAPI backend for the Enterprise IT Support Agentic RAG system.

Endpoints:
    GET  /health          - liveness/readiness check
    POST /chat            - ask a question, get routed answer + source + ticket (if any)
    POST /ingest           - re-run ingestion of the policy corpus
    GET  /tickets           - list tickets created so far (demo/admin view)
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agent_graph import run_agent
from app.ingest import run_ingest
from app.ticketing import list_tickets
from app.vector_store import collection_count

app = FastAPI(title="Enterprise IT Support Agentic RAG", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    requester: str = "anonymous"


class ChatResponse(BaseModel):
    answer: str
    source: str
    kb_hits: int
    web_hits: int
    ticket_id: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "kb_chunks_indexed": collection_count()}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="question must not be empty")

    try:
        state = run_agent(req.question, requester=req.requester)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {e}")

    return ChatResponse(
        answer=state.get("answer", "Sorry, something went wrong."),
        source=state.get("source", "unknown"),
        kb_hits=len(state.get("kb_results", []) or []),
        web_hits=len(state.get("web_results", []) or []),
        ticket_id=(state.get("ticket") or {}).get("id"),
    )


@app.post("/ingest")
def ingest():
    try:
        count = run_ingest()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {e}")
    return {"chunks_ingested": count}


@app.get("/tickets")
def tickets():
    return {"tickets": list_tickets()}
