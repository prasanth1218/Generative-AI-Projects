"""
Structured data lives in PostgreSQL: users, document metadata, chunk-to-vector
links, and audit logs. This matches Q40/Q41 -- relational DB for anything that
needs consistency and querying; vectors themselves live in Chroma, not here.
"""
import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, Integer, ForeignKey, Text, Float
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


def gen_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default="user")  # "user" | "admin"
    created_at = Column(DateTime, default=datetime.utcnow)


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=gen_uuid)
    title = Column(String, nullable=False)
    source_type = Column(String, default="upload")  # upload | connector | url
    domain_tag = Column(String, default="general")  # e.g. finance, hr, policy
    access_level = Column(String, default="internal")
    file_path = Column(String, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    chunks = relationship("DocumentChunkMeta", back_populates="document")


class DocumentChunkMeta(Base):
    """
    Links a Postgres record to its vector representation in Chroma.
    Postgres stores the pointer + metadata; Chroma stores the embedding + text.
    """
    __tablename__ = "document_chunks_meta"

    id = Column(String, primary_key=True, default=gen_uuid)
    document_id = Column(String, ForeignKey("documents.id"))
    chunk_index = Column(Integer, nullable=False)
    chroma_id = Column(String, nullable=False)

    document = relationship("Document", back_populates="chunks")


class AuditLog(Base):
    """
    Every query is logged: what was asked, what was retrieved, what came back,
    and how long it took. This is what makes Q54 (monitoring) and Q52 (trust)
    more than a claim in the interview -- it's an actual table you can query live.
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, nullable=True)
    query_text = Column(Text, nullable=False)
    retrieved_doc_ids = Column(Text, nullable=True)  # comma-separated chroma ids
    response_text = Column(Text, nullable=True)
    used_llm = Column(Integer, default=1)  # 0/1 -- did this query actually call the LLM
    is_grounded = Column(Integer, default=1)  # 0/1 -- did validator pass it as grounded
    latency_ms = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(String, primary_key=True, default=gen_uuid)
    audit_log_id = Column(String, ForeignKey("audit_logs.id"))
    rating = Column(Integer, nullable=False)  # 1 = up, -1 = down
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
