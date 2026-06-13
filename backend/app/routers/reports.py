from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.database import get_db
from app.models import Deal, Document, Issue, DDReport
from app.config import settings
from app.services.report_generator import generate_report_content, generate_docx_report

router = APIRouter(prefix="/api/deals/{deal_id}/reports", tags=["reports"])


@router.post("/generate")
def generate_report(deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")

    docs = db.query(Document).filter(Document.deal_id == deal_id).all()
    issues = db.query(Issue).filter(Issue.deal_id == deal_id).all()

    analysis_summary = ""
    for d in docs:
        analysis_summary += f"\nDocument: {d.filename} (Workstream: {d.workstream}, Status: {d.status})\n"
        if d.summary:
            analysis_summary += f"Summary: {d.summary}\n"

    issue_summary = ""
    for i in issues:
        issue_summary += f"- [{i.severity.upper()}] {i.title} ({i.workstream or 'N/A'}, Status: {i.status})\n"
        if i.description:
            issue_summary += f"  {i.description}\n"
        if i.recommendation:
            issue_summary += f"  Recommendation: {i.recommendation}\n"

    report_content = generate_report_content(
        deal_name=deal.deal_name,
        target_company=deal.target_company,
        acquirer=deal.acquirer or "N/A",
        analysis_summary=analysis_summary,
        issue_summary=issue_summary,
    )

    report_dir = Path(settings.storage_dir) / deal_id / "reports"
    report_path = report_dir / "due_diligence_report.docx"

    generate_docx_report(report_content, str(report_path), deal.deal_name)

    report = DDReport(
        deal_id=deal_id,
        report_path=str(report_path),
        status="completed",
        summary=report_content[:500] if report_content else "",
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {"report_id": report.id, "status": "completed", "path": f"/api/deals/{deal_id}/reports/{report.id}/download"}


@router.get("/{report_id}/download")
def download_report(deal_id: str, report_id: str, db: Session = Depends(get_db)):
    report = db.query(DDReport).filter(DDReport.id == report_id, DDReport.deal_id == deal_id).first()
    if not report or not report.report_path:
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(report.report_path, filename=f"dd_report_{deal_id}.docx")
