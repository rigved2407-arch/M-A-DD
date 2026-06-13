from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Issue, Deal, Document
from app.schemas import IssueCreate, IssueOut

router = APIRouter(prefix="/api/deals/{deal_id}/issues", tags=["issues"])


@router.get("", response_model=list[IssueOut])
def list_issues(
    deal_id: str,
    severity: str = None,
    status: str = None,
    workstream: str = None,
    db: Session = Depends(get_db),
):
    q = db.query(Issue).filter(Issue.deal_id == deal_id)
    if severity:
        q = q.filter(Issue.severity == severity)
    if status:
        q = q.filter(Issue.status == status)
    if workstream:
        q = q.filter(Issue.workstream == workstream)
    return q.order_by(Issue.created_at.desc()).all()


@router.post("", response_model=IssueOut)
def create_issue(deal_id: str, data: IssueCreate, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    if data.document_id:
        doc = db.query(Document).filter(Document.id == data.document_id).first()
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

    issue = Issue(deal_id=deal_id, **data.model_dump())
    db.add(issue)
    deal.issue_count = db.query(Issue).filter(Issue.deal_id == deal_id).count()
    db.commit()
    db.refresh(issue)
    return issue


@router.patch("/{issue_id}", response_model=IssueOut)
def update_issue(deal_id: str, issue_id: str, data: IssueCreate, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.deal_id == deal_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(issue, key, val)
    db.commit()
    db.refresh(issue)
    return issue


@router.patch("/{issue_id}/status")
def update_issue_status(deal_id: str, issue_id: str, status: str, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.deal_id == deal_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    issue.status = status
    db.commit()
    return {"ok": True}


@router.delete("/{issue_id}")
def delete_issue(deal_id: str, issue_id: str, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.deal_id == deal_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    db.delete(issue)
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal:
        deal.issue_count = db.query(Issue).filter(Issue.deal_id == deal_id).count()
    db.commit()
    return {"ok": True}
