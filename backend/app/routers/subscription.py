from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_org
from app.models import Organization, PLANS, User
from app.services.usage_limits import get_plan

router = APIRouter(prefix="/api/subscription", tags=["subscription"])


@router.get("/plans")
def list_plans():
    return [{"id": k, **v} for k, v in PLANS.items()]


@router.get("/current")
def current_subscription(org: Organization = Depends(get_current_org)):
    plan = get_plan(org)
    return {
        "plan": org.plan,
        "limits": plan,
        "usage": {
            "deals": org.deal_count,
            "users": org.user_count,
            "documents": org.document_count,
            "storage_mb": org.storage_used_mb,
        },
    }
