import os
import shutil
import uuid

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.session import get_db
from backend.db.models import Document
from backend.ingestion.indexer import ingest_document
from backend.api.auth import verify_api_key

router = APIRouter(prefix="/documents", tags=["documents"])

UPLOAD_DIR = "./data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}


@router.post("/upload", dependencies=[Depends(verify_api_key)])
async def upload_document(
    file: UploadFile = File(...),
    domain_tag: str = Form("general"),
    access_level: str = Form("internal"),
    db: Session = Depends(get_db),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    safe_name = f"{uuid.uuid4()}{ext}"
    dest_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = ingest_document(
        db=db,
        file_path=dest_path,
        title=file.filename,
        domain_tag=domain_tag,
        access_level=access_level,
    )

    return {
        "document_id": doc.id,
        "title": doc.title,
        "domain_tag": doc.domain_tag,
        "status": "indexed",
    }


@router.get("/", dependencies=[Depends(verify_api_key)])
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "domain_tag": d.domain_tag,
            "access_level": d.access_level,
            "uploaded_at": d.uploaded_at.isoformat() if d.uploaded_at else None,
        }
        for d in docs
    ]
