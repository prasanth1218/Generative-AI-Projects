"""
Minimal observability endpoint -- reads straight from the audit_logs table.
Implements Q54 (monitoring) as a real, queryable endpoint instead of a slide.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models import AuditLog
from backend.api.auth import verify_api_key

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/", dependencies=[Depends(verify_api_key)])
def get_metrics(db: Session = Depends(get_db)):
    total = db.query(func.count(AuditLog.id)).scalar() or 0
    grounded = db.query(func.count(AuditLog.id)).filter(AuditLog.is_grounded == 1).scalar() or 0
    avg_latency = db.query(func.avg(AuditLog.latency_ms)).scalar() or 0
    llm_calls = db.query(func.count(AuditLog.id)).filter(AuditLog.used_llm == 1).scalar() or 0

    return {
        "total_queries": total,
        "grounded_responses": grounded,
        "grounded_rate": round(grounded / total, 3) if total else 0,
        "llm_calls": llm_calls,
        "llm_call_rate": round(llm_calls / total, 3) if total else 0,
        "avg_latency_ms": round(avg_latency, 2),
    }
