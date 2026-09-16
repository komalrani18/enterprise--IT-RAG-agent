#!/usr/bin/env bash
set -e

# Ingest the policy corpus on first boot (idempotent-ish: re-embeds every cold start,
# which is fine for a small demo corpus; swap for a persisted volume + check for larger ones).
cd /app/backend
python -m app.ingest || echo "[start.sh] Ingestion failed or found no docs — continuing anyway."

exec supervisord -c /etc/supervisor/conf.d/supervisord.conf
