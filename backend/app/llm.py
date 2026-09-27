"""
Provider-agnostic LLM and embedding clients.

Keeping these behind small factory functions means agent_graph.py never needs to
know whether it's talking to Groq, OpenAI, or a local Ollama server.
"""
from functools import lru_cache
from typing import List

from app.config import settings


# ---------------------------------------------------------------------------
# LLM chat completion
# ---------------------------------------------------------------------------
def get_chat_client():
    """Returns an object with a `.invoke(messages: list[dict]) -> str` method."""
    provider = settings.llm_provider

    if provider == "groq":
        from groq import Groq

        client = Groq(api_key=settings.groq_api_key)

        class _GroqChat:
            def invoke(self, messages):
                resp = client.chat.completions.create(
                    model=settings.llm_model,
                    messages=messages,
                    temperature=0.2,
                )
                return resp.choices[0].message.content

        return _GroqChat()

    if provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)

        class _OpenAIChat:
            def invoke(self, messages):
                resp = client.chat.completions.create(
                    model=settings.llm_model,
                    messages=messages,
                    temperature=0.2,
                )
                return resp.choices[0].message.content

        return _OpenAIChat()

    if provider == "ollama":
        import requests

        class _OllamaChat:
            def invoke(self, messages):
                resp = requests.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json={
                        "model": settings.ollama_model,
                        "messages": messages,
                        "stream": False,
                    },
                    timeout=120,
                )
                resp.raise_for_status()
                return resp.json()["message"]["content"]

        return _OllamaChat()

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


# ---------------------------------------------------------------------------
# Embeddings
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1)
def _local_embedder():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(settings.local_embedding_model)


class EmbeddingClient:
    def __init__(self):
        self.provider = settings.embedding_provider
        if self.provider == "openai":
            from openai import OpenAI

            self._client = OpenAI(api_key=settings.openai_api_key)
        elif self.provider == "local":
            self._model = _local_embedder()
        else:
            raise ValueError(f"Unknown EMBEDDING_PROVIDER: {self.provider}")

    @property
    def dimension(self) -> int:
        if self.provider == "local":
            return self._model.get_sentence_embedding_dimension()
        # text-embedding-3-small = 1536 dims
        return 1536

    def embed(self, texts: List[str]) -> List[List[float]]:
        if self.provider == "local":
            return self._model.encode(texts, show_progress_bar=False).tolist()
        resp = self._client.embeddings.create(
            model=settings.openai_embedding_model, input=texts
        )
        return [d.embedding for d in resp.data]

    def embed_one(self, text: str) -> List[float]:
        return self.embed([text])[0]


@lru_cache(maxsize=1)
def get_embedding_client() -> EmbeddingClient:
    return EmbeddingClient()
