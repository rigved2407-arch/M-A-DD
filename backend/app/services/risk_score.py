from sqlalchemy.orm import Session
from app.models import Document

_SEVERITY_WEIGHTS = {"high": 10, "medium": 4, "low": 1, "info": 0}


def compute_risk_score(db: Session, deal_id: str) -> float:
    docs = db.query(Document).filter(Document.deal_id == deal_id).all()
    doc_count = len(docs)
    if doc_count == 0:
        return 0.0

    total_weight = 0
    for d in docs:
        flags = d.red_flags or []
        for flag in flags:
            sev = flag.get("severity", "medium") if isinstance(flag, dict) else "medium"
            total_weight += _SEVERITY_WEIGHTS.get(sev, 4)

    max_possible = doc_count * 10
    score = round((total_weight / max_possible) * 100, 1) if max_possible else 0.0
    return min(100.0, score)
