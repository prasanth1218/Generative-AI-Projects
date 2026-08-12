"""
Single place that knows how to turn text into vectors. Both the indexer
(write path) and the retriever (read path) import from here so embeddings
are always generated the same way -- a common bug source is using different
models/settings for indexing vs. querying, which silently breaks retrieval.

Implementation note: this uses Chroma's built-in ONNX MiniLM embedding
function rather than the full `sentence-transformers` + PyTorch stack.
Same underlying MiniLM model family, ~10x smaller install footprint, no GPU/
torch dependency -- a deliberately lighter choice for a fast, low-resource
deployment. If you later need a different embedding model (e.g. a domain-
specific one), only this file changes.
"""
from functools import lru_cache
from typing import List


@lru_cache(maxsize=1)
def get_embedding_function():
    from chromadb.utils import embedding_functions
    return embedding_functions.DefaultEmbeddingFunction()


def embed_texts(texts: List[str]) -> List[List[float]]:
    fn = get_embedding_function()
    return fn(texts)


def embed_query(text: str) -> List[float]:
    return embed_texts([text])[0]
