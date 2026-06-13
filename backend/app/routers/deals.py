import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Deal
from app.schemas import DealCreate, DealOut

router = APIRouter(prefix="/api/deals", tags=["deals"])


@router.get("", response_model=list[DealOut])
def list_deals(db: Session = Depends(get_db)):
    return db.query(Deal).order_by(Deal.created_at.desc()).all()


@router.post("", response_model=DealOut)
def create_deal(data: DealCreate, db: Session = Depends(get_db)):
    deal = Deal(**data.model_dump())
    db.add(deal)
    db.commit()
    db.refresh(deal)
    return deal


@router.get("/{deal_id}", response_model=DealOut)
def get_deal(deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return deal


@router.put("/{deal_id}", response_model=DealOut)
def update_deal(deal_id: str, data: DealCreate, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    for key, val in data.model_dump().items():
        setattr(deal, key, val)
    db.commit()
    db.refresh(deal)
    return deal


@router.delete("/{deal_id}")
def delete_deal(deal_id: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    db.delete(deal)
    db.commit()
    return {"ok": True}


@router.patch("/{deal_id}/status")
def update_deal_status(deal_id: str, status: str, db: Session = Depends(get_db)):
    deal = db.query(Deal).filter(Deal.id == deal_id).first()
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    deal.status = status
    db.commit()
    return {"ok": True}
