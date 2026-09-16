"""
Chunk + embed the IT/HR policy corpus and upsert into Qdrant.

Usage:
    python -m app.ingest                 # ingest default policies_dir
    python -m app.ingest --dir /path     # ingest a different directory
"""
import argparse
import glob
import os

from app.config import settings
from app.vector_store import upsert_chunks, ensure_collection


def chunk_text(text: str, chunk_size: int, overlap: int):
    """Simple word-based sliding-window chunker (dependency-free, deterministic)."""
    words = text.split()
    if not words:
        return []
    chunks = []
    step = max(chunk_size - overlap, 1)
    for start in range(0, len(words), step):
        window = words[start : start + chunk_size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + chunk_size >= len(words):
            break
    return chunks


def load_documents(directory: str):
    paths = sorted(glob.glob(os.path.join(directory, "**", "*.md"), recursive=True))
    paths += sorted(glob.glob(os.path.join(directory, "**", "*.txt"), recursive=True))
    docs = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            docs.append({"source": os.path.basename(path), "text": f.read()})
    return docs


def run_ingest(directory: str = None):
    directory = directory or settings.policies_dir
    print(f"[ingest] Loading documents from: {directory}")
    docs = load_documents(directory)
    if not docs:
        print("[ingest] No .md/.txt documents found. Nothing to ingest.")
        return 0

    ensure_collection()

    all_chunks = []
    for doc in docs:
        pieces = chunk_text(doc["text"], settings.chunk_size, settings.chunk_overlap)
        for i, piece in enumerate(pieces):
            all_chunks.append({"text": piece, "source": doc["source"], "chunk_index": i})
        print(f"[ingest]   {doc['source']}: {len(pieces)} chunk(s)")

    total = 0
    batch_size = 32
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        total += upsert_chunks(batch)

    print(f"[ingest] Done. Upserted {total} chunks from {len(docs)} document(s) "
          f"into collection '{settings.qdrant_collection}'.")
    return total


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", dest="directory", default=None)
    args = parser.parse_args()
    run_ingest(args.directory)
