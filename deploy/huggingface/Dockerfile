# Hugging Face Spaces expects a single container exposing one port (7860 by default).
# This Dockerfile runs the FastAPI backend (internal, port 8000) and the Streamlit
# frontend (public, port 7860) side by side using a tiny process supervisor.
#
# To use: create a new Space with SDK = "Docker", then copy this entire repo's
# contents into the Space repo with this file at the Space root as `Dockerfile`
# (or set the Space's Dockerfile path to deploy/huggingface/Dockerfile).
# Add your API keys as Space "Secrets" (Settings -> Repository secrets) — they are
# injected as environment variables automatically.

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl supervisor \
    && rm -rf /var/lib/apt/lists/*

# --- Backend deps ---
COPY backend/requirements.txt ./backend-requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r backend-requirements.txt

# --- Frontend deps ---
COPY frontend/requirements.txt ./frontend-requirements.txt
RUN pip install --no-cache-dir -r frontend-requirements.txt

# --- App code ---
COPY backend/app ./backend/app
COPY frontend/streamlit_app.py ./frontend/streamlit_app.py
COPY data ./data

ENV POLICIES_DIR=/app/data/policies
ENV QDRANT_PATH=/app/qdrant_data
ENV BACKEND_URL=http://localhost:8000
ENV PYTHONPATH=/app/backend

COPY deploy/huggingface/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY deploy/huggingface/start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Hugging Face Spaces routes traffic to port 7860
EXPOSE 7860

CMD ["/app/start.sh"]
