"""
Thin wrapper around Qdrant for upserting and querying policy chunk embeddings.

Uses embedded/local Qdrant (a file on disk, no server needed) unless QDRANT_URL is
set, in which case it talks to a real Qdrant server / Qdrant Cloud instance.
"""
import uuid
from functools import lru_cache
from typing import List, Dict, Any

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import settings
from app.llm import get_embedding_client


@lru_cache(maxsize=1)
def get_qdrant_client() -> QdrantClient:
    if settings.qdrant_url:
        return QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
    return QdrantClient(path=settings.qdrant_path)


def ensure_collection():
    client = get_qdrant_client()
    dim = get_embedding_client().dimension
    existing = [c.name for c in client.get_collections().collections]
    if settings.qdrant_collection not in existing:
        client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=qmodels.VectorParams(size=dim, distance=qmodels.Distance.COSINE),
        )


def upsert_chunks(chunks: List[Dict[str, Any]]):
    """chunks: list of {"text": str, "source": str, "chunk_index": int}"""
    client = get_qdrant_client()
    embedder = get_embedding_client()
    ensure_collection()

    vectors = embedder.embed([c["text"] for c in chunks])
    points = [
        qmodels.PointStruct(
            id=str(uuid.uuid4()),
            vector=vec,
            payload={
                "text": chunk["text"],
                "source": chunk["source"],
                "chunk_index": chunk["chunk_index"],
            },
        )
        for chunk, vec in zip(chunks, vectors)
    ]
    client.upsert(collection_name=settings.qdrant_collection, points=points)
    return len(points)


def search(query: str, top_k: int = None) -> List[Dict[str, Any]]:
    """Returns list of {"text", "source", "score"} sorted by relevance."""
    top_k = top_k or settings.retrieval_top_k
    client = get_qdrant_client()
    embedder = get_embedding_client()
    ensure_collection()

    query_vec = embedder.embed_one(query)
    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vec,
        limit=top_k,
    )
    return [
        {
            "text": r.payload["text"],
            "source": r.payload["source"],
            "score": r.score,
        }
        for r in results
    ]


def collection_count() -> int:
    client = get_qdrant_client()
    try:
        info = client.get_collection(settings.qdrant_collection)
        return info.points_count or 0
    except Exception:
        return 0
