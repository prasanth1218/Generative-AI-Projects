from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.db.session import init_db, SessionLocal
from backend.api import documents, query, metrics
from backend.ingestion.indexer import ensure_sample_docs_indexed

app = FastAPI(
    title="Enterprise AI Research Agent",
    description=(
        "Retrieval-augmented research assistant over enterprise documents. "
        "Modular layers: ingestion -> retrieval -> orchestration -> validation."
    ),
    version="1.0.0",
)

# Allow the local frontend dev server to call the API during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this for real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(query.router)
app.include_router(metrics.router)


@app.on_event("startup")
def on_startup():
    init_db()

    # Self-healing: on free-tier hosts, local disk (and therefore Chroma's
    # vector store) doesn't survive a restart, even though Postgres does.
    # Detect that mismatch and re-index the sample docs automatically so
    # the deployed demo is always queryable without a manual re-upload.
    db = SessionLocal()
    try:
        ensure_sample_docs_indexed(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}
