"""
Centralized, environment-driven configuration.

Nothing else in the codebase should call os.getenv directly for these values —
import `settings` from here instead, so all config lives in one place.
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


def _bool(val: str, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    # --- LLM ---
    llm_provider: str = os.getenv("LLM_PROVIDER", "groq").lower()
    llm_model: str = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3")

    # --- Embeddings ---
    embedding_provider: str = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    local_embedding_model: str = os.getenv(
        "LOCAL_EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    openai_embedding_model: str = os.getenv(
        "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
    )

    # --- Vector store ---
    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_path: str = os.getenv("QDRANT_PATH", "./qdrant_data")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "it_policies")

    # --- Retrieval / grading ---
    retrieval_top_k: int = int(os.getenv("RETRIEVAL_TOP_K", "4"))
    retrieval_score_threshold: float = float(
        os.getenv("RETRIEVAL_SCORE_THRESHOLD", "0.25")
    )

    # --- Web search fallback ---
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

    # --- Ticketing ---
    ticket_store_path: str = os.getenv("TICKET_STORE_PATH", "./tickets.json")
    ticket_queue_email: str = os.getenv("TICKET_QUEUE_EMAIL", "it-support@example.com")

    # --- Chunking ---
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))

    # --- Data ---
    policies_dir: str = os.getenv("POLICIES_DIR", "../data/policies")


settings = Settings()
