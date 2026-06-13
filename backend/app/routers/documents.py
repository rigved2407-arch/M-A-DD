import uuid
import os
import re
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document, Deal
from app.schemas import DocumentOut
from app.config import settings
from app.services.document_parser import parse_document_raw, extract_metadata
from app.services.classifier import classify_document
from app.services.encryption import encrypt_file_bytes

MAGIC_BYTES: dict[str, bytes] = {
    ".pdf": b"%PDF",
    ".docx": b"PK\x03\x04",
    ".xlsx": b"PK\x03\x04",
    ".pptx": b"PK\x03\x04",
}


def _validate_file_signature(content: bytes, ext: str) -> bool:
    if ext not in MAGIC_BYTES:
        return True
    return len(content) >= len(MAGIC_BYTES[ext]) and content[: len(MAGIC_BYTES[ext])] == MAGIC_BYTES[ext]


router = APIRouter(prefix="/api/deals/{deal_id}/documents", tags=["documents"])


@router.get("", response_model=list[DocumentOut])
def list_documents(deal_id: str, workstream: str = None, db: Session = Depends(get_db)):
    q = db.query(Document).filter(Document.deal_id == deal_id)
    if workstream:
        q = q.filter(Document.workstream == workstream)
    return q.order_by(Document.created_at.desc()).all()


@router.get("/{doc_id}", response_model=DocumentOut)
def get_document(deal_id: str, doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.deal_id == deal_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.post("/upload", response_model=DocumentOut)
async def upload_document(deal_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    raw_name = (file.filename or "upload")
    safe_filename = Path(raw_name).name
    safe_filename = re.sub(r'[^\w\-_. ]', '_', safe_filename)
    safe_filename = safe_filename.lstrip('.') or "upload"

    allowed = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".md", ".pptx"}
    ext = Path(safe_filename).suffix.lower()
    if ext not in allowed:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    storage = Path(settings.storage_dir) / deal_id
    storage.mkdir(parents=True, exist_ok=True)

    doc_id = str(uuid.uuid4())
    save_path = storage / f"{doc_id}{ext}"
    content = await file.read()

    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    if not _validate_file_signature(content, ext):
        raise HTTPException(status_code=400, detail=f"File signature mismatch for {ext} — possible file type spoofing")

    text = parse_document_raw(content, ext) or ""

    if settings.encrypt_documents:
        encrypted_content = encrypt_file_bytes(content)
        with open(save_path, "wb") as f:
            f.write(encrypted_content)
    else:
        with open(save_path, "wb") as f:
            f.write(content)

    workstream = classify_document(safe_filename, text)
    metadata = extract_metadata(text, safe_filename)

    doc = Document(
        id=doc_id,
        deal_id=deal_id,
        filename=safe_filename,
        file_path=str(save_path),
        file_type=ext,
        file_size=len(content),
        workstream=workstream,
        content_text=text,
        extracted_data=metadata,
        status="classified",
    )
    db.add(doc)
    deal.document_count = db.query(Document).filter(Document.deal_id == deal_id).count()
    db.commit()
    db.refresh(doc)
    return doc


@router.delete("/{doc_id}")
def delete_document(deal_id: str, doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.deal_id == deal_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.file_path and os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    db.delete(doc)
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal:
        deal.document_count = db.query(Document).filter(Document.deal_id == deal_id).count()
    db.commit()
    return {"ok": True}
