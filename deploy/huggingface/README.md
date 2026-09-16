---
title: Enterprise IT Support Agentic RAG
emoji: 🛠️
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# Deploying to Hugging Face Spaces

1. Create a new Space at huggingface.co/new-space, SDK = **Docker**.
2. Push this whole repository to the Space's git remote, with this file's
   frontmatter (above) at the root `README.md`, and set the Space's Dockerfile
   path to `deploy/huggingface/Dockerfile` (Space settings → "Dockerfile path"),
   or copy that file to the repo root as `Dockerfile`.
3. In Space Settings → **Repository secrets**, add whichever of these you use:
   - `GROQ_API_KEY` (or `OPENAI_API_KEY` if `LLM_PROVIDER=openai`)
   - `TAVILY_API_KEY` (optional, enables the web-search fallback)
   - `LLM_PROVIDER`, `LLM_MODEL` if you want to override the defaults
4. Push. The Space builds the combined image, ingests the sample policy docs on
   boot, and serves the Streamlit chat UI on the Space's public URL.

Note: Spaces free-tier containers are ephemeral — the embedded Qdrant index is
rebuilt from `data/policies/` on every cold start via `start.sh`. For a larger
corpus, either persist `/app/qdrant_data` with a Space's persistent storage
add-on, or point `QDRANT_URL`/`QDRANT_API_KEY` at an external Qdrant Cloud
cluster instead (same env vars as the Docker Compose / DigitalOcean setups).
