from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import DealActivity
from app.schemas import DealActivityOut

router = APIRouter(prefix="/api/deals/{deal_id}/activity", tags=["activity"])


def log_activity(db: Session, deal_id: str, user_id: str | None, action: str, details: dict | None = None, ip: str | None = None):
    activity = DealActivity(
        deal_id=deal_id,
        user_id=user_id,
        action=action,
        details=details or {},
        ip_address=ip,
    )
    db.add(activity)
    db.commit()


@router.get("", response_model=list[DealActivityOut])
def list_activity(deal_id: str, db: Session = Depends(get_db)):
    return (
        db.query(DealActivity)
        .filter(DealActivity.deal_id == deal_id)
        .order_by(DealActivity.created_at.desc())
        .limit(100)
        .all()
    )
