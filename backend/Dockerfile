# NOTE: build this image with the project root as the build context, e.g.:
#   docker build -f backend/Dockerfile -t it-rag-backend .
# (docker-compose.yml in this repo is already configured that way)
FROM python:3.11-slim

WORKDIR /app

# System deps for sentence-transformers / torch CPU wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY data ./data

ENV POLICIES_DIR=/app/data/policies
ENV QDRANT_PATH=/app/qdrant_data

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
