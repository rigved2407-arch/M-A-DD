from fastapi import Request, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Organization


def get_current_org(request: Request, db: Session = Depends(get_db)) -> Organization:
    org_id = getattr(request.state, "org_id", None)
    if not org_id:
        org_id = request.headers.get("X-Organization-ID")
    if not org_id:
        from app.database import get_default_org
        org_id = get_default_org()
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


def require_role(*roles: str):
    def _check(request: Request):
        user_role = getattr(request.state, "user_role", None)
        if not user_role or user_role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return True
    return _check
