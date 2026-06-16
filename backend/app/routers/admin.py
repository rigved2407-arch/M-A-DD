from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_org, require_role
from app.models import Organization, User
from app.services.password_utils import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users")
def list_users(org: Organization = Depends(get_current_org), db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    users = db.query(User).filter(User.organization_id == org.id).all()
    return [{"id": u.id, "email": u.email, "name": u.name, "role": u.role, "is_active": u.is_active, "last_login_at": u.last_login_at} for u in users]


@router.post("/users")
def invite_user(email: str, name: str, role: str = "associate", org: Organization = Depends(get_current_org), db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    from app.services.usage_limits import check_user_limit
    ok, msg = check_user_limit(org)
    if not ok:
        raise HTTPException(status_code=403, detail=msg)
    existing = db.query(User).filter(User.email == email, User.organization_id == org.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    user = User(organization_id=org.id, email=email, name=name, role=role, password_hash=hash_password("changeme123"))
    db.add(user)
    db.commit()
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}


@router.patch("/users/{user_id}/role")
def update_role(user_id: str, role: str, org: Organization = Depends(get_current_org), db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id, User.organization_id == org.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.role = role
    db.commit()
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}


@router.delete("/users/{user_id}")
def remove_user(user_id: str, org: Organization = Depends(get_current_org), db: Session = Depends(get_db), _=Depends(require_role("admin"))):
    user = db.query(User).filter(User.id == user_id, User.organization_id == org.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"ok": True}


@router.get("/billing")
def billing_info(org: Organization = Depends(get_current_org)):
    from app.services.usage_limits import get_plan
    plan = get_plan(org)
    return {"plan": org.plan, "price": plan["price"], "trial_days_left": 0}
