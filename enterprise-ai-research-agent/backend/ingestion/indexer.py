"""
Ties the ingestion pipeline together: load -> chunk -> embed -> store in
Chroma, and write the pointer metadata into Postgres. This is the function
that runs whenever a new document is added (Q46 -- new data without code
changes: adding a document is a function call / API upload, not a redeploy).
"""
import os
import uuid

from sqlalchemy.orm import Session

from backend.ingestion.loader import load_document
from backend.ingestion.chunker import chunk_text
from backend.retrieval.embeddings import embed_texts
from backend.retrieval import vector_store
from backend.db.models import Document, DocumentChunkMeta


def ingest_document(
    db: Session,
    file_path: str,
    title: str,
    domain_tag: str = "general",
    access_level: str = "internal",
) -> Document:
    # 1. Persist document record
    doc = Document(
        title=title,
        source_type="upload",
        domain_tag=domain_tag,
        access_level=access_level,
        file_path=file_path,
    )
    db.add(doc)
    db.flush()  # get doc.id without committing yet

    # 2. Load raw text
    raw_text = load_document(file_path)

    # 3. Chunk
    chunks = chunk_text(raw_text)
    if not chunks:
        db.commit()
        return doc

    # 4. Embed
    embeddings = embed_texts(chunks)

    # 5. Store vectors in Chroma with metadata pointing back to Postgres doc
    chroma_ids = [f"{doc.id}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "document_id": doc.id,
            "title": title,
            "domain_tag": domain_tag,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]
    vector_store.add_chunks(
        ids=chroma_ids, embeddings=embeddings, documents=chunks, metadatas=metadatas
    )

    # 6. Store chunk pointers in Postgres
    for i, chroma_id in enumerate(chroma_ids):
        db.add(DocumentChunkMeta(document_id=doc.id, chunk_index=i, chroma_id=chroma_id))

    db.commit()
    db.refresh(doc)
    return doc
