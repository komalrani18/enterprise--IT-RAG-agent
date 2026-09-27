"""
External tools the agent graph can call: web search (fallback #1) and
ticket creation (fallback #2).
"""
from typing import List, Dict

from app.config import settings
from app.ticketing import create_ticket as _create_ticket


def web_search(query: str, max_results: int = 4) -> List[Dict[str, str]]:
    """Runs a Tavily web search. Returns [] if no API key is configured."""
    if not settings.tavily_api_key:
        return []
    try:
        from tavily import TavilyClient

        client = TavilyClient(api_key=settings.tavily_api_key)
        resp = client.search(query=query, max_results=max_results, search_depth="advanced")
        return [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
            }
            for r in resp.get("results", [])
        ]
    except Exception as e:
        print(f"[tools.web_search] Tavily search failed: {e}")
        return []


def file_it_ticket(question: str, context_summary: str, requester: str = "anonymous") -> dict:
    return _create_ticket(question=question, context_summary=context_summary, requester=requester)
