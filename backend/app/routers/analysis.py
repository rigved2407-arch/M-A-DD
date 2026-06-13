import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Document, Issue, Deal
from app.services.analyzer import analyze_document

router = APIRouter(prefix="/api/deals/{deal_id}/analysis", tags=["analysis"])


@router.post("/documents/{doc_id}")
def analyze_document_endpoint(deal_id: str, doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.deal_id == deal_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not doc.content_text:
        raise HTTPException(status_code=400, detail="Document has no extracted text")

    result = analyze_document(doc.filename, doc.workstream, doc.content_text)

    doc.summary = result.get("summary")
    doc.extracted_data = {
        "key_terms": result.get("key_terms", []),
        "risks": result.get("risks", ""),
    }

    red_flags = result.get("red_flags", [])
    doc.red_flags = red_flags

    for flag in red_flags:
        issue = Issue(
            deal_id=deal_id,
            document_id=doc_id,
            workstream=doc.workstream,
            title=flag.get("title", "Red flag"),
            description=flag.get("description", ""),
            severity=flag.get("severity", "medium"),
            category=flag.get("category", "other"),
            reference_text=flag.get("reference_text", ""),
            recommendation=flag.get("recommendation", ""),
        )
        db.add(issue)

    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal:
        deal.issue_count = db.query(Issue).filter(Issue.deal_id == deal_id).count()
        all_docs = db.query(Document).filter(Document.deal_id == deal_id).all()
        scores = [d.red_flags for d in all_docs if d.red_flags]
        total_flags = sum(len(f) for f in scores if f)
        deal.risk_score = min(100, total_flags * 10) if total_flags else 0

    doc.status = "analyzed"
    db.commit()
    db.refresh(doc)

    return {
        "document_id": doc_id,
        "summary": doc.summary,
        "key_terms": result.get("key_terms", []),
        "risks": result.get("risks", ""),
        "red_flags_count": len(red_flags),
        "issues_created": len(red_flags),
    }


@router.post("/all")
def analyze_all_documents(deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    docs = db.query(Document).filter(Document.deal_id == deal_id, Document.status != "analyzed").all()
    results = []
    for doc in docs:
        try:
            result = analyze_document(doc.filename, doc.workstream, doc.content_text)
            doc.summary = result.get("summary")
            doc.extracted_data = {"key_terms": result.get("key_terms", []), "risks": result.get("risks", "")}
            red_flags = result.get("red_flags", [])
            doc.red_flags = red_flags
            for flag in red_flags:
                db.add(Issue(
                    deal_id=deal_id, document_id=doc.id, workstream=doc.workstream,
                    title=flag.get("title", "Red flag"), description=flag.get("description", ""),
                    severity=flag.get("severity", "medium"), category=flag.get("category", "other"),
                    reference_text=flag.get("reference_text", ""), recommendation=flag.get("recommendation", ""),
                ))
            doc.status = "analyzed"
            results.append({"doc_id": doc.id, "status": "ok", "flags": len(red_flags)})
        except Exception as e:
            results.append({"doc_id": doc.id, "status": "error", "error": str(e)})

    deal.issue_count = db.query(Issue).filter(Issue.deal_id == deal_id).count()
    all_docs = db.query(Document).filter(Document.deal_id == deal_id).all()
    total_flags = sum(len(d.red_flags or []) for d in all_docs)
    deal.risk_score = min(100, total_flags * 10) if total_flags else 0
    db.commit()

    return {"total_analyzed": len(results), "results": results, "total_issues": deal.issue_count, "risk_score": deal.risk_score}
