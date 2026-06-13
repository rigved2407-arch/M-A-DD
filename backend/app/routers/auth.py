import uuid
import secrets
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserOut
from app.config import settings
from app.services.password_utils import hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

_JWT_SECRET = settings.api_key or secrets.token_urlsafe(48)
_JWT_ALG = "HS256"
_JWT_EXP = 86400  # 24 hours


def create_jwt(user_id: str, organization_id: str, role: str) -> str:
    payload = {
        "sub": user_id,
        "org": organization_id,
        "role": role,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(seconds=_JWT_EXP),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALG)


def decode_jwt(token: str) -> dict | None:
    try:
        return jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALG])
    except jwt.PyJWTError:
        return None


class LoginInput(BaseModel):
    email: str
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


@router.post("/login", response_model=LoginOut)
def login(data: LoginInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.password_hash or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_jwt(user.id, user.organization_id, user.role)

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return LoginOut(
        access_token=token,
        user=UserOut(
            id=user.id, email=user.email, name=user.name,
            role=user.role, is_active=user.is_active,
            created_at=user.created_at, last_login_at=user.last_login_at,
        ),
    )
