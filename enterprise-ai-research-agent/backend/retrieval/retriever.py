"""
The retrieval layer's public interface. Orchestration code calls
`retrieve(query)` and gets back a clean list of results -- it never touches
Chroma or the embedding model directly. This isolation is what lets you swap
the vector DB or embedding model without touching orchestration (Q42).
"""
from dataclasses import dataclass
from typing import List

from backend.retrieval.embeddings import embed_query
from backend.retrieval import vector_store


@dataclass
class RetrievedChunk:
    text: str
    title: str
    document_id: str
    chunk_index: int
    distance: float


def retrieve(query_text: str, top_k: int = None) -> List[RetrievedChunk]:
    embedding = embed_query(query_text)
    raw = vector_store.query(embedding, top_k=top_k)

    results: List[RetrievedChunk] = []
    if not raw or not raw.get("ids") or not raw["ids"][0]:
        return results

    docs = raw["documents"][0]
    metas = raw["metadatas"][0]
    dists = raw["distances"][0]

    for text, meta, dist in zip(docs, metas, dists):
        results.append(
            RetrievedChunk(
                text=text,
                title=meta.get("title", "unknown"),
                document_id=meta.get("document_id", ""),
                chunk_index=meta.get("chunk_index", -1),
                distance=dist,
            )
        )
    return results
