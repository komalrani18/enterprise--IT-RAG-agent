#!/usr/bin/env bash
# Runs the ingestion pipeline inside the backend container (Docker Compose setup).
# Usage: ./scripts/run_ingest.sh
set -euo pipefail

docker compose run --rm backend python -m app.ingest
