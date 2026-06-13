from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import Document, QASession, Deal
from app.services.qa_service import answer_question
from app.schemas import QAResponse

router = APIRouter(prefix="/api/deals/{deal_id}/qa", tags=["qa"])


class QuestionInput(BaseModel):
    question: str
    documents: list[str] = None


@router.post("", response_model=QAResponse)
def ask_question(deal_id: str, data: QuestionInput, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    if data.documents:
        docs = db.query(Document).filter(
            Document.id.in_(data.documents),
            Document.deal_id == deal_id,
            Document.content_text.isnot(None),
        ).all()
    else:
        docs = db.query(Document).filter(
            Document.deal_id == deal_id,
            Document.content_text.isnot(None),
        ).all()

    if not docs:
        raise HTTPException(status_code=400, detail="No documents with content found for this deal")

    docs_text = [{"filename": d.filename, "text": d.content_text or ""} for d in docs]
    result = answer_question(data.question, docs_text)

    session = QASession(
        deal_id=deal_id,
        question=data.question,
        answer=result.get("answer", ""),
        citations=result.get("citations", []),
    )
    db.add(session)
    db.commit()

    return QAResponse(
        question=data.question,
        answer=result.get("answer", ""),
        citations=result.get("citations", []),
    )


@router.get("/history", response_model=list[QAResponse])
def qa_history(deal_id: str, db: Session = Depends(get_db)):
    sessions = db.query(QASession).filter(
        QASession.deal_id == deal_id
    ).order_by(QASession.created_at.desc()).limit(50).all()

    return [
        QAResponse(question=s.question, answer=s.answer or "", citations=s.citations or [])
        for s in sessions
    ]
