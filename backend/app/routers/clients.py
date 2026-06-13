import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Client, Deal
from app.schemas import ClientCreate, ClientOut

router = APIRouter(prefix="/api/clients", tags=["clients"])


@router.get("", response_model=list[ClientOut])
def list_clients(db: Session = Depends(get_db)):
    return db.query(Client).order_by(Client.created_at.desc()).all()


@router.post("", response_model=ClientOut)
def create_client(data: ClientCreate, db: Session = Depends(get_db)):
    client = Client(id=str(uuid.uuid4()), **data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientOut)
def get_client(client_id: str, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientOut)
def update_client(client_id: str, data: ClientCreate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    for key, val in data.model_dump().items():
        setattr(client, key, val)
    db.commit()
    db.refresh(client)
    return client


@router.delete("/{client_id}")
def delete_client(client_id: str, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    db.delete(client)
    db.commit()
    return {"ok": True}


@router.get("/{client_id}/deals")
def get_client_deals(client_id: str, db: Session = Depends(get_db)):
    deals = db.query(Deal).filter(Deal.client_id == client_id).order_by(Deal.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "deal_name": d.deal_name,
            "target_company": d.target_company,
            "status": d.status,
            "risk_score": d.risk_score,
            "document_count": d.document_count,
            "issue_count": d.issue_count,
            "created_at": d.created_at.isoformat(),
        }
        for d in deals
    ]
