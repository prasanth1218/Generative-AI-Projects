"""
Ties the ingestion pipeline together: load -> chunk -> embed -> store in
Chroma, and write the pointer metadata into Postgres. This is the function
that runs whenever a new document is added (Q46 -- new data without code
changes: adding a document is a function call / API upload, not a redeploy).
"""
import os
import uuid
from pathlib import Path

from sqlalchemy.orm import Session

from backend.ingestion.loader import load_document
from backend.ingestion.chunker import chunk_text
from backend.retrieval.embeddings import embed_texts
from backend.retrieval import vector_store
from backend.db.models import Document, DocumentChunkMeta

SAMPLE_DOCS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "sample_docs"


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


def ensure_sample_docs_indexed(db: Session) -> None:
    """
    Self-healing startup check for free-tier hosting (e.g. Render's free plan),
    where local disk storage -- and therefore ChromaDB's persisted vectors --
    does not survive a service restart. Postgres data DOES survive (it's a
    managed, persistent database), so after a restart we can end up with
    document *metadata* rows in Postgres but an empty, unsearchable vector
    store in Chroma -- retrieval silently returns nothing until this runs.

    On every startup: if Chroma's collection is empty, clear any stale
    document metadata rows (they point to vectors that no longer exist) and
    re-ingest the bundled sample documents fresh. This keeps the demo always
    queryable without a manual re-upload step after every cold start.
    """
    try:
        collection = vector_store.get_collection()
        vector_count = collection.count()
    except Exception:
        vector_count = 0

    if vector_count > 0:
        return  # Chroma already has data -- nothing to heal

    # Clear stale metadata rows that point to now-missing vectors
    db.query(DocumentChunkMeta).delete()
    db.query(Document).delete()
    db.commit()

    if not SAMPLE_DOCS_DIR.exists():
        return

    domain_by_filename = {
        "leave_policy.txt": "hr",
        "it_security_policy.txt": "security",
        "expense_policy.txt": "finance",
    }

    for file_path in sorted(SAMPLE_DOCS_DIR.glob("*.txt")):
        domain_tag = domain_by_filename.get(file_path.name, "general")
        try:
            ingest_document(
                db=db,
                file_path=str(file_path),
                title=file_path.name,
                domain_tag=domain_tag,
            )
        except Exception as e:
            # Don't let one bad sample file block the whole startup
            print(f"[startup] Failed to auto-index {file_path.name}: {e}")