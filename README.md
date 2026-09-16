# Enterprise IT Support Agentic RAG

A multi-agent Retrieval-Augmented Generation system for enterprise IT/HR support.
Instead of a single-shot chatbot, this uses a **LangGraph** agent workflow that:

1. Retrieves from a vector store of IT/HR policy documents (Qdrant).
2. Grades whether the retrieved context actually answers the question.
3. Falls back to a live web search (Tavily) if the internal KB is insufficient.
4. Falls back further to auto-creating an IT support ticket if neither source resolves the issue.

```
User Question
     │
     ▼
[retrieve]  ── query Qdrant (policy embeddings)
     │
     ▼
[grade_kb]  ── LLM judges: does this context answer the question?
     │
   ┌─┴──────────────┐
   │yes              │no
   ▼                 ▼
[answer_kb]     [web_search]  ── Tavily search
   │                 │
   ▼                 ▼
  END          [grade_web]  ── LLM judges: does the web result answer it?
                    │
                ┌───┴───────────┐
                │yes             │no
                ▼                ▼
           [answer_web]     [create_ticket]  ── files an IT ticket, returns ticket ID
                │                │
                ▼                ▼
               END              END
```

## Project layout

```
it_rag_agent/
├── data/policies/          # Sample IT/HR policy docs to ingest (replace with your own)
├── backend/
│   ├── app/
│   │   ├── config.py       # Env-driven config: LLM provider, embeddings, vector DB
│   │   ├── vector_store.py # Qdrant client wrapper
│   │   ├── ingest.py       # Chunk + embed + upsert policy docs
│   │   ├── tools.py        # Tavily web search + ticket creation tools
│   │   ├── ticketing.py    # Simple file-backed ticket store (swap for ServiceNow/Jira)
│   │   ├── agent_graph.py  # LangGraph state machine (the multi-agent workflow)
│   │   └── main.py         # FastAPI app exposing /chat, /health, /ingest
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── streamlit_app.py    # Chat UI, hits backend /chat endpoint
│   ├── requirements.txt
│   └── Dockerfile
├── deploy/
│   ├── digitalocean/app.yaml
│   └── huggingface/        # Combined single-container Space (backend+frontend)
├── docker-compose.yml
└── scripts/run_ingest.sh
```

## Model & embedding choices (all swappable via `.env`)

- **LLM**: defaults to Groq's Llama 3 (`llama-3.1-70b-versatile`) via `LLM_PROVIDER=groq`.
  Also supports `LLM_PROVIDER=openai` (any OpenAI model) or `LLM_PROVIDER=ollama`
  (fully local Llama 3 via a running Ollama server — no API key needed).
- **Embeddings**: defaults to a local, open-source `sentence-transformers/all-MiniLM-L6-v2`
  model (no API key, runs on CPU). Set `EMBEDDING_PROVIDER=openai` to use OpenAI embeddings instead.
- **Vector DB**: Qdrant. Runs embedded/local (`QDRANT_PATH=./qdrant_data`, zero setup) by
  default, or point at a real Qdrant server / Qdrant Cloud with `QDRANT_URL` + `QDRANT_API_KEY`.

## Quickstart (local, no Docker)

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # fill in at least one LLM key
python -m app.ingest       # chunks + embeds data/policies into Qdrant
uvicorn app.main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000
streamlit run streamlit_app.py
```

## Quickstart (Docker Compose — backend + frontend + Qdrant server)

```bash
cp .env.example .env   # fill in keys
docker compose up --build
# Streamlit UI:  http://localhost:8501
# Backend docs:  http://localhost:8000/docs
```

The `ingest` step runs automatically as a one-off container the first time you run
`docker compose up`; re-run it any time policy docs change:

```bash
docker compose run --rm backend python -m app.ingest
```

## Deploying

### DigitalOcean App Platform
See `deploy/digitalocean/app.yaml`. It defines two services (backend, frontend) built
from this repo's Dockerfiles, plus the required env vars. Push this repo to GitHub, then:

```bash
doctl apps create --spec deploy/digitalocean/app.yaml
```

Note: App Platform doesn't run a persistent Qdrant container well as a "service" with a
volume by default — the recommended path is to use **Qdrant Cloud** (set `QDRANT_URL` /
`QDRANT_API_KEY` in the app spec) rather than local/embedded mode in production.

### Hugging Face Spaces (single container)
Spaces expects one container per Space. `deploy/huggingface/` contains a combined
Dockerfile that runs the FastAPI backend and Streamlit frontend in one container via
a tiny process supervisor, exposing Streamlit on port 7860 (the port HF Spaces expects).
Copy its contents to the root of a new "Docker" Space, add your secrets (API keys) in
the Space's settings, and push.

## Environment variables

See `.env.example` for the full list: LLM provider + key, embedding provider, Qdrant
connection, Tavily key for web search fallback, and ticketing config.

## Extending this for real use

- Swap `ticketing.py`'s file-backed store for a real ITSM API call (ServiceNow, Jira
  Service Management, Zendesk) — the interface (`create_ticket(...)`) is already isolated.
- Add authentication (SSO) in front of the FastAPI app before exposing it beyond a demo.
- Add per-department or per-sensitivity-level access control on retrieved chunks if your
  policy corpus contains restricted documents.
- Swap the relevance "grader" node from an LLM call to a cheaper cross-encoder reranker
  if latency/cost at scale becomes a concern.
