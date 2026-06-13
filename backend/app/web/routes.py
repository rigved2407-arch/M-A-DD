from pathlib import Path
from fastapi import APIRouter, Depends, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Deal, Document, Issue, QASession, DDReport, Client
from app.config import settings
from app.services.document_parser import parse_document_raw
from app.services.classifier import classify_document
from app.services.analyzer import analyze_document
from app.services.qa_service import answer_question
from app.services.report_generator import generate_report_content, generate_docx_report
from app.services.dpdp_compliance import record_consent, get_consent_history, withdraw_consent, create_data_subject_request, get_dpdp_summary
from app.services.compliance_checklist import get_compliance_checklist, get_compliance_summary

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")
router = APIRouter(tags=["web"])

WORKSTREAMS = ["legal", "financial", "commercial", "tax", "hr", "it", "environmental", "insurance", "regulatory", "other"]


def _counts(deal_id: str, db: Session):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        return {"docs": 0, "analyzed": 0, "issues": 0, "high_issues": 0}
    docs = db.query(Document).filter(Document.deal_id == deal_id).all()
    issues = db.query(Issue).filter(Issue.deal_id == deal_id).all()
    return {
        "docs": len(docs),
        "analyzed": sum(1 for d in docs if d.status == "analyzed"),
        "issues": len(issues),
        "high_issues": sum(1 for i in issues if i.severity == "high"),
    }


def _render(template: str, request: Request, **kwargs):
    return templates.TemplateResponse(template, {"request": request, "settings": settings, **kwargs})


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    deals_list = db.query(Deal).order_by(Deal.created_at.desc()).all()
    return _render("index.html", request, deals=deals_list)


@router.get("/deals/new", response_class=HTMLResponse)
def new_deal_page(request: Request, db: Session = Depends(get_db)):
    clients = db.query(Client).order_by(Client.name).all()
    return _render("deals/new.html", request, clients=clients)


@router.post("/web/deals/create")
def create_deal_web(
    request: Request,
    deal_name: str = Form(...),
    target_company: str = Form(...),
    acquirer: str = Form(""),
    deal_type: str = Form("M&A"),
    description: str = Form(""),
    client_id: str = Form(""),
    db: Session = Depends(get_db),
):
    import uuid
    deal = Deal(id=str(uuid.uuid4()), deal_name=deal_name, target_company=target_company,
                acquirer=acquirer, deal_type=deal_type, description=description,
                client_id=client_id if client_id else None)
    db.add(deal)
    db.commit()
    return RedirectResponse(url=f"/deals/{deal.id}", status_code=303)


@router.get("/deals/{deal_id}", response_class=HTMLResponse)
def deal_detail(request: Request, deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        return RedirectResponse(url="/")

    docs = db.query(Document).filter(Document.deal_id == deal_id).order_by(Document.created_at.desc()).all()
    issues = db.query(Issue).filter(Issue.deal_id == deal_id).order_by(Issue.created_at.desc()).all()
    qa_history = db.query(QASession).filter(QASession.deal_id == deal_id).order_by(QASession.created_at.desc()).limit(10).all()
    report = db.query(DDReport).filter(DDReport.deal_id == deal_id).order_by(DDReport.created_at.desc()).first()
    counts = _counts(deal_id, db)

    by_workstream = {}
    for d in docs:
        ws = d.workstream or "other"
        if ws not in by_workstream:
            by_workstream[ws] = []
        by_workstream[ws].append(d)

    return _render("deals/detail.html", request, deal=deal, docs=docs, issues=issues,
                   qa_history=qa_history, report=report, counts=counts,
                   by_workstream=by_workstream, workstreams=WORKSTREAMS)


@router.post("/web/deals/{deal_id}/upload", response_class=HTMLResponse)
async def upload_doc_web(
    request: Request, deal_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    import uuid
    import re
    from pathlib import Path as P

    raw_name = (file.filename or "upload")
    safe_name = P(raw_name).name
    safe_name = re.sub(r'[^\w\-_. ]', '_', safe_name)
    safe_name = safe_name.lstrip('.') or "upload"

    allowed = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".csv", ".txt", ".md", ".pptx"}
    ext = P(safe_name).suffix.lower()
    if ext not in allowed:
        return HTMLResponse("Unsupported file type", status_code=400)

    storage = P(settings.storage_dir) / deal_id
    storage.mkdir(parents=True, exist_ok=True)

    doc_id = str(uuid.uuid4())
    save_path = storage / f"{doc_id}{ext}"
    content = await file.read()

    text = parse_document_raw(content, ext) or ""

    with open(save_path, "wb") as f:
        f.write(content)

    workstream = classify_document(safe_name, text)

    doc = Document(id=doc_id, deal_id=deal_id, filename=safe_name,
                   file_path=str(save_path), file_type=ext, file_size=len(content),
                   workstream=workstream, content_text=text, status="classified")
    db.add(doc)
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal:
        deal.document_count = db.query(Document).filter(Document.deal_id == deal_id).count()
    db.commit()

    return RedirectResponse(url=f"/deals/{deal_id}", status_code=303)


@router.post("/web/deals/{deal_id}/analyze/{doc_id}")
def analyze_doc_web(request: Request, deal_id: str, doc_id: str, db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.deal_id == deal_id).first()
    if not doc or not doc.content_text:
        return HTMLResponse("Document not found", status_code=404)

    result = analyze_document(doc.filename, doc.workstream, doc.content_text)
    doc.summary = result.get("summary")
    doc.extracted_data = {"key_terms": result.get("key_terms", []), "risks": result.get("risks", "")}
    red_flags = result.get("red_flags", [])
    doc.red_flags = red_flags

    for flag in red_flags:
        db.add(Issue(deal_id=deal_id, document_id=doc_id, workstream=doc.workstream,
                     title=flag.get("title", "Red flag"), description=flag.get("description", ""),
                     severity=flag.get("severity", "medium"), category=flag.get("category", "other"),
                     reference_text=flag.get("reference_text", ""), recommendation=flag.get("recommendation", "")))

    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal:
        deal.issue_count = db.query(Issue).filter(Issue.deal_id == deal_id).count()
        all_docs = db.query(Document).filter(Document.deal_id == deal_id).all()
        total_flags = sum(len(d.red_flags or []) for d in all_docs)
        deal.risk_score = min(100, total_flags * 10) if total_flags else 0

    doc.status = "analyzed"
    db.commit()
    return RedirectResponse(url=f"/deals/{deal_id}", status_code=303)


@router.post("/web/deals/{deal_id}/analyze-all")
def analyze_all_web(request: Request, deal_id: str, db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.deal_id == deal_id, Document.status != "analyzed").all()
    for doc in docs:
        try:
            result = analyze_document(doc.filename, doc.workstream, doc.content_text)
            doc.summary = result.get("summary")
            doc.extracted_data = {"key_terms": result.get("key_terms", []), "risks": result.get("risks", "")}
            red_flags = result.get("red_flags", [])
            doc.red_flags = red_flags
            for flag in red_flags:
                db.add(Issue(deal_id=deal_id, document_id=doc.id, workstream=doc.workstream,
                             title=flag.get("title", "Red flag"), description=flag.get("description", ""),
                             severity=flag.get("severity", "medium"), category=flag.get("category", "other"),
                             reference_text=flag.get("reference_text", ""), recommendation=flag.get("recommendation", "")))
            doc.status = "analyzed"
        except Exception:
            pass

    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal:
        deal.issue_count = db.query(Issue).filter(Issue.deal_id == deal_id).count()
        all_docs = db.query(Document).filter(Document.deal_id == deal_id).all()
        total_flags = sum(len(d.red_flags or []) for d in all_docs)
        deal.risk_score = min(100, total_flags * 10) if total_flags else 0
    db.commit()
    return RedirectResponse(url=f"/deals/{deal_id}", status_code=303)


@router.post("/web/deals/{deal_id}/qa")
def ask_question_web(
    request: Request, deal_id: str,
    question: str = Form(...),
    db: Session = Depends(get_db),
):
    docs = db.query(Document).filter(
        Document.deal_id == deal_id, Document.content_text.isnot(None)
    ).all()
    if not docs:
        return RedirectResponse(url=f"/deals/{deal_id}", status_code=303)

    docs_text = [{"filename": d.filename, "text": d.content_text or ""} for d in docs]
    result = answer_question(question, docs_text)

    session = QASession(deal_id=deal_id, question=question,
                        answer=result.get("answer", ""),
                        citations=result.get("citations", []))
    db.add(session)
    db.commit()

    return RedirectResponse(url=f"/deals/{deal_id}", status_code=303)


@router.get("/dpdp/privacy", response_class=HTMLResponse)
def dpdp_privacy(request: Request):
    return _render("dpdp/privacy.html", request)


@router.get("/dpdp/consent", response_class=HTMLResponse)
def dpdp_consent(request: Request, db: Session = Depends(get_db)):
    email = request.query_params.get("email")
    consents = get_consent_history(db, email)
    return _render("dpdp/consent.html", request, consents=consents)


@router.post("/dpdp/consent/{consent_id}/withdraw")
def dpdp_withdraw_consent(request: Request, consent_id: str, db: Session = Depends(get_db)):
    withdraw_consent(db, consent_id)
    return RedirectResponse(url="/dpdp/consent", status_code=303)


@router.get("/dpdp/data-request", response_class=HTMLResponse)
def dpdp_data_request_page(request: Request):
    return _render("dpdp/data_request.html", request)


@router.post("/dpdp/data-request")
def dpdp_submit_data_request(
    request: Request,
    request_type: str = Form("access"),
    principal_name: str = Form(...),
    principal_email: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    result = create_data_subject_request(db, request_type, principal_name, principal_email, description)
    return _render("dpdp/data_request.html", request, submitted=True, result=result)


@router.get("/dpdp/compliance", response_class=HTMLResponse)
def dpdp_compliance_dashboard(request: Request, db: Session = Depends(get_db)):
    summary = get_dpdp_summary(db)
    return _render("dpdp/compliance.html", request, summary=summary)


@router.get("/deals/{deal_id}/compliance", response_class=HTMLResponse)
def deal_compliance(request: Request, deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        return RedirectResponse(url="/")
    checklist = get_compliance_checklist(deal.deal_type)
    return _render("deals/compliance.html", request, deal=deal, checklist=checklist, workstreams=WORKSTREAMS)


@router.post("/web/deals/{deal_id}/issues/new")
def create_issue_web(
    request: Request, deal_id: str,
    title: str = Form(...), description: str = Form(""),
    severity: str = Form("medium"), workstream: str = Form("other"),
    document_id: str = Form(""), recommendation: str = Form(""),
    db: Session = Depends(get_db),
):
    issue = Issue(deal_id=deal_id, title=title, description=description,
                  severity=severity, workstream=workstream,
                  document_id=document_id if document_id else None,
                  recommendation=recommendation)
    db.add(issue)
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if deal:
        deal.issue_count = db.query(Issue).filter(Issue.deal_id == deal_id).count()
    db.commit()
    return RedirectResponse(url=f"/deals/{deal_id}", status_code=303)


@router.post("/web/deals/{deal_id}/issues/{issue_id}/status")
def update_issue_status_web(request: Request, deal_id: str, issue_id: str,
                            status: str = Form("open"), db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.id == issue_id, Issue.deal_id == deal_id).first()
    if issue:
        issue.status = status
        db.commit()
    return RedirectResponse(url=f"/deals/{deal_id}", status_code=303)


@router.post("/web/deals/{deal_id}/report")
def generate_report_web(request: Request, deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        return RedirectResponse(url="/")

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

    report_content = generate_report_content(deal.deal_name, deal.target_company,
                                              deal.acquirer or "N/A", analysis_summary, issue_summary)

    report_dir = Path(settings.storage_dir) / deal_id / "reports"
    report_path = report_dir / "due_diligence_report.docx"
    generate_docx_report(report_content, str(report_path), deal.deal_name)

    report = DDReport(deal_id=deal_id, report_path=str(report_path),
                      status="completed", summary=report_content[:500])
    db.add(report)
    db.commit()

    return RedirectResponse(url=f"/deals/{deal_id}", status_code=303)
