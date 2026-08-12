# Architecture

## Layers

1. **Frontend (React)** — query input, answer display, source citations,
   document upload, live metrics strip.
2. **Backend API (FastAPI)** — request validation, routing, auth, response
   shaping. No business logic lives here — it delegates to orchestration.
3. **Ingestion pipeline** — `loader.py` (file → text) → `chunker.py`
   (text → overlapping chunks) → `indexer.py` (chunks → embeddings → Chroma
   + Postgres metadata pointer).
4. **Retrieval layer** — `embeddings.py` (text → vector) + `vector_store.py`
   (Chroma wrapper) + `retriever.py` (public interface: query text in,
   ranked chunks out).
5. **Orchestration layer** — `pipeline.py` sequences four steps:
   - `query_understanding.py` — cheap rule-based check: is this worth
     retrieving/generating for at all?
   - `retriever.py` — semantic search against indexed documents
   - `validator.py` (pre-check) — is retrieval good enough to justify an
     LLM call? If not, return an honest "insufficient information" response
     and stop here — no LLM call made.
   - `generator.py` — builds a grounded prompt (context + question,
     explicit instruction not to guess) and calls the LLM provider
6. **LLM layer** — `base.py` defines the provider interface; `groq_provider.py`
   and `mock_provider.py` implement it; `factory.py` picks one based on
   config, with automatic fallback to mock if Groq isn't configured.
7. **Storage**
   - PostgreSQL: `users`, `documents`, `document_chunks_meta`, `audit_logs`,
     `feedback` — anything structured, queryable, needing consistency.
   - ChromaDB: chunk text + embeddings + metadata — optimized for semantic
     similarity search.
   - Local disk (`data/uploads`): raw uploaded files — stands in for object
     storage (S3/Blob) in a full deployment.
8. **Observability** — every query writes an `AuditLog` row (query text,
   retrieved doc ids, grounded/ungrounded, LLM used or not, latency).
   `/metrics` aggregates these into grounded rate, LLM call rate, and
   average latency — queryable live, not just described.

## Information flow (matches assessment Q38)

```
User query
   │
   ▼
FastAPI /query endpoint (auth + validation)
   │
   ▼
query_understanding.classify_query()
   │  fails? → return "not a research question", log, stop (no LLM call)
   ▼  passes
retriever.retrieve()  → top-k chunks from Chroma
   │
   ▼
validator.validate()  → is retrieval strong enough?
   │  no? → return "insufficient information", log, stop (no LLM call)
   ▼  yes
generator.generate_answer()  → grounded prompt → LLM provider → answer text
   │
   ▼
Response + sources returned to frontend, AuditLog row written
```

Two "early exit" points are deliberate — they are the direct implementation
of the "reduce unnecessary LLM calls" and "don't answer from assumptions"
assessment answers, not just design intentions.

## Why modular, not monolithic

Each arrow above is a function call across a module boundary, not inline
logic. Concretely:
- Swap Chroma for another vector DB → only `vector_store.py` changes.
- Swap Groq for another LLM → only `llm/factory.py` + a new provider file.
- Add a new file type to ingest → only `loader.py` changes.
- Add real JWT auth → only `api/auth.py` changes.

This is what "new capabilities without redesigning the system" (assessment
Q69, Q71) looks like as actual code rather than a claim.

## Scaling path (not built, but designed for — Q43)

At 100k+ documents, the changes would be:
- Ingestion becomes async: a queue (e.g. Celery + Redis, or AWS SQS + Lambda)
  processes uploads instead of the synchronous `ingest_document()` call.
- Embedding generation runs in parallel batches.
- Chroma (single-node, file-based) would move to a hosted vector DB or a
  sharded/clustered deployment.
- Postgres would get connection pooling and read replicas for the audit log
  table under heavy query volume.
- Backend would scale horizontally behind a load balancer; the pipeline code
  itself doesn't change, since orchestration has no in-memory state.
