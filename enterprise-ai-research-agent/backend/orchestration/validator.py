"""
Post-generation validation. Deliberately simple, rule-based checks --
not another LLM call (that would defeat the point of Q49). This is the
concrete implementation of Q44/Q45/Q51: don't return a confident-sounding
answer when retrieval was weak, and always surface which sources backed it.
"""
from dataclasses import dataclass
from typing import List

from backend.retrieval.retriever import RetrievedChunk

# Chroma returns cosine/L2 distance depending on config; lower = more similar.
# This threshold is intentionally conservative -- tune against your own corpus.
MAX_ACCEPTABLE_DISTANCE = 1.0


@dataclass
class ValidationResult:
    is_grounded: bool
    reason: str
    sources: List[str]


def validate(chunks: List[RetrievedChunk]) -> ValidationResult:
    if not chunks:
        return ValidationResult(
            is_grounded=False, reason="no_chunks_retrieved", sources=[]
        )

    good_chunks = [c for c in chunks if c.distance <= MAX_ACCEPTABLE_DISTANCE]
    if not good_chunks:
        return ValidationResult(
            is_grounded=False, reason="retrieved_chunks_too_dissimilar", sources=[]
        )

    sources = sorted({c.title for c in good_chunks})
    return ValidationResult(is_grounded=True, reason="ok", sources=sources)
