from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models import AuditLog
from backend.orchestration.pipeline import run_pipeline
from backend.api.auth import verify_api_key

router = APIRouter(prefix="/query", tags=["query"])


class QueryRequest(BaseModel):
    question: str
    top_k: int | None = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[str]
    is_grounded: bool
    used_llm: bool
    latency_ms: float


@router.post("/", response_model=QueryResponse, dependencies=[Depends(verify_api_key)])
def query_endpoint(req: QueryRequest, db: Session = Depends(get_db)):
    result = run_pipeline(req.question, top_k=req.top_k)

    # Audit log every query -- this is what makes Q40/Q54/Q52 verifiable,
    # not just something you claim in the interview.
    log = AuditLog(
        query_text=req.question,
        retrieved_doc_ids=",".join(result.retrieved_doc_ids),
        response_text=result.answer,
        used_llm=1 if result.used_llm else 0,
        is_grounded=1 if result.is_grounded else 0,
        latency_ms=result.latency_ms,
    )
    db.add(log)
    db.commit()

    return QueryResponse(
        answer=result.answer,
        sources=result.sources,
        is_grounded=result.is_grounded,
        used_llm=result.used_llm,
        latency_ms=result.latency_ms,
    )
