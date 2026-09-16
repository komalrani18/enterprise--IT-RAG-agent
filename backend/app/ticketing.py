"""
Minimal file-backed IT ticket store.

This is intentionally isolated behind `create_ticket()` / `list_tickets()` so it can
be swapped for a real ITSM integration (ServiceNow, Jira Service Management, Zendesk)
without touching the agent graph — just change the implementation of create_ticket().
"""
import json
import os
import uuid
from datetime import datetime, timezone
from filelock import FileLock

from app.config import settings


def _load() -> list:
    if not os.path.exists(settings.ticket_store_path):
        return []
    with open(settings.ticket_store_path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def _save(tickets: list):
    with open(settings.ticket_store_path, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2)


def create_ticket(question: str, context_summary: str, requester: str = "anonymous") -> dict:
    lock_path = settings.ticket_store_path + ".lock"
    with FileLock(lock_path):
        tickets = _load()
        ticket = {
            "id": f"TICK-{uuid.uuid4().hex[:8].upper()}",
            "status": "open",
            "requester": requester,
            "question": question,
            "context_summary": context_summary,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "queue": settings.ticket_queue_email,
        }
        tickets.append(ticket)
        _save(tickets)
    return ticket


def list_tickets() -> list:
    return _load()
