"""
Thin wrapper around ChromaDB so the rest of the app never talks to Chroma's
client API directly. If you ever swap Chroma for Pinecone/FAISS/pgvector,
this is the only file that changes -- that's the point of the "retrieval
layer as a replaceable module" design (Q42, Q71).
"""
from functools import lru_cache
from typing import List, Dict, Any

import chromadb

from backend.config.settings import settings


@lru_cache(maxsize=1)
def get_client():
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)


def get_collection():
    client = get_client()
    return client.get_or_create_collection(name=settings.chroma_collection_name)


def add_chunks(
    ids: List[str],
    embeddings: List[List[float]],
    documents: List[str],
    metadatas: List[Dict[str, Any]],
):
    collection = get_collection()
    collection.add(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)


def query(embedding: List[float], top_k: int = None) -> Dict[str, Any]:
    top_k = top_k or settings.top_k
    collection = get_collection()
    return collection.query(query_embeddings=[embedding], n_results=top_k)
