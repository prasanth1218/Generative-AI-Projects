"""
Splits raw text into overlapping chunks before embedding.

Why overlap: without it, a fact split across a chunk boundary becomes
unretrievable from either chunk. A small overlap (default 50 words) fixes
that at almost no extra storage cost.

This is intentionally word-based, not a tokenizer-perfect split -- simple,
fast, dependency-free, and good enough for a 2-day build. Swappable later
for a tokenizer-aware chunker without touching any other module.
"""
from typing import List

from backend.config.settings import settings


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        if chunk.strip():
            chunks.append(chunk.strip())
        if end >= len(words):
            break
        start = end - overlap  # step back by overlap

    return chunks
