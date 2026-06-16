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


class RegisterInput(BaseModel):
    email: str
    name: str
    password: str
    firm_name: str = "My Firm"


@router.post("/register")
def register(data: RegisterInput, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    from app.models import Organization

    org = Organization(name=data.firm_name)
    org.user_count = 1
    db.add(org)
    db.flush()

    user = User(
        organization_id=org.id,
        email=data.email,
        name=data.name,
        role="admin",
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_jwt(user.id, user.organization_id, user.role)

    from app.services.email_service import send_welcome_email
    try:
        send_welcome_email(user.name, user.email)
    except Exception:
        pass

    return LoginOut(
        access_token=token,
        user=UserOut(
            id=user.id, email=user.email, name=user.name,
            role=user.role, is_active=user.is_active,
            created_at=user.created_at, last_login_at=user.last_login_at,
        ),
    )


class ForgotPasswordInput(BaseModel):
    email: str


class ResetPasswordInput(BaseModel):
    token: str
    password: str


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordInput, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        return {"message": "If this email is registered, a reset link has been sent."}

    from app.models import PasswordResetToken

    reset_token = secrets.token_urlsafe(48)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    token_record = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
    )
    db.add(token_record)
    db.commit()

    from app.services.email_service import send_password_reset
    try:
        send_password_reset(user.name, user.email, reset_token)
    except Exception:
        pass

    return {"message": "If this email is registered, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordInput, db: Session = Depends(get_db)):
    from app.models import PasswordResetToken

    token_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == data.token,
        PasswordResetToken.used_at.is_(None),
        PasswordResetToken.expires_at > datetime.now(timezone.utc),
    ).first()

    if not token_record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.password_hash = hash_password(data.password)
    token_record.used_at = datetime.now(timezone.utc)
    db.commit()

    return {"message": "Password reset successfully. You can now log in with your new password."}
