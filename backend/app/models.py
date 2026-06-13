import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, Float, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


def _uuid():
    return str(uuid.uuid4())


def _utcnow():
    return datetime.now(timezone.utc)


WORKSTREAMS = [
    "legal", "financial", "commercial", "tax",
    "hr", "it", "environmental", "insurance", "regulatory", "other",
]

USER_ROLES = ["partner", "associate", "reviewer", "admin"]


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String(256), nullable=False)
    email = Column(String(256))
    address = Column(Text)
    created_at = Column(DateTime, default=_utcnow)


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(256), unique=True, nullable=False, index=True)
    name = Column(String(256), nullable=False)
    role = Column(String(32), default="associate")
    password_hash = Column(String(256))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=_utcnow)
    last_login_at = Column(DateTime, nullable=True)


class Client(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(256), nullable=False)
    email = Column(String(256))
    phone = Column(String(64))
    company = Column(String(256))
    address = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)


class Deal(Base):
    __tablename__ = "deals"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = Column(String, ForeignKey("clients.id", ondelete="SET NULL"), nullable=True, index=True)
    deal_name = Column(String(256), nullable=False)
    target_company = Column(String(256), nullable=False)
    acquirer = Column(String(256), default="")
    deal_type = Column(String(64), default="M&A")
    description = Column(Text)
    status = Column(String(32), default="active")
    document_count = Column(Integer, default=0)
    issue_count = Column(Integer, default=0)
    risk_score = Column(Float)
    assigned_to = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    documents = relationship("Document", back_populates="deal", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="deal", cascade="all, delete-orphan")
    qa_sessions = relationship("QASession", back_populates="deal", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    deal_id = Column(String, ForeignKey("deals.id"), nullable=False)
    filename = Column(String(512), nullable=False)
    file_path = Column(String(1024))
    file_type = Column(String(16))
    file_size = Column(Integer, default=0)
    workstream = Column(String(64), default="other")
    status = Column(String(32), default="uploaded")
    content_text = Column(Text)
    summary = Column(Text)
    extracted_data = Column(JSON)
    red_flags = Column(JSON)
    uploaded_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    deal = relationship("Deal", back_populates="documents")
    issues = relationship("Issue", back_populates="document", cascade="all, delete-orphan")


class Issue(Base):
    __tablename__ = "issues"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    deal_id = Column(String, ForeignKey("deals.id"), nullable=False)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    workstream = Column(String(64))
    title = Column(String(256), nullable=False)
    description = Column(Text)
    severity = Column(String(16), default="medium")
    status = Column(String(32), default="open")
    category = Column(String(64))
    reference_text = Column(Text)
    recommendation = Column(Text)
    assignee = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)
    deal = relationship("Deal", back_populates="issues")
    document = relationship("Document", back_populates="issues")


class QASession(Base):
    __tablename__ = "qa_sessions"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    deal_id = Column(String, ForeignKey("deals.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    citations = Column(JSON)
    asked_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=_utcnow)
    deal = relationship("Deal", back_populates="qa_sessions")


class DDReport(Base):
    __tablename__ = "dd_reports"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    deal_id = Column(String, ForeignKey("deals.id"), nullable=False)
    report_path = Column(String(1024))
    report_format = Column(String(16), default="docx")
    status = Column(String(32), default="generating")
    summary = Column(Text)
    generated_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=_utcnow)


class DealActivity(Base):
    __tablename__ = "deal_activities"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    deal_id = Column(String, ForeignKey("deals.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(64), nullable=False)
    details = Column(JSON)
    ip_address = Column(String(64))
    created_at = Column(DateTime, default=_utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    method = Column(String(16))
    path = Column(String(512))
    query_params = Column(String(512))
    status_code = Column(Integer)
    duration_ms = Column(Integer)
    ip_address = Column(String(64))
    user_agent = Column(String(512))
    created_at = Column(DateTime, default=_utcnow)


class DPDPConsent(Base):
    __tablename__ = "dpdp_consents"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    principal_name = Column(String(256), nullable=False)
    principal_email = Column(String(256), nullable=False)
    organization = Column(String(256))
    purpose = Column(String(256), nullable=False)
    ip_address = Column(String(64))
    consent_version = Column(String(32), default="1.0")
    consented_at = Column(DateTime, default=_utcnow)
    withdrawn_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class DataSubjectRequest(Base):
    __tablename__ = "dpdp_data_requests"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    request_type = Column(String(64), nullable=False)
    principal_name = Column(String(256), nullable=False)
    principal_email = Column(String(256), nullable=False)
    description = Column(Text)
    status = Column(String(32), default="pending")
    requested_at = Column(DateTime, default=_utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text)


class BreachNotification(Base):
    __tablename__ = "dpdp_breach_notifications"
    id = Column(String, primary_key=True, default=_uuid)
    organization_id = Column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    breach_type = Column(String(128), nullable=False)
    description = Column(Text, nullable=False)
    affected_count = Column(Integer, default=0)
    notified_board = Column(Boolean, default=True)
    notified_principals = Column(Boolean, default=True)
    notification_sent_at = Column(DateTime, default=_utcnow)
    resolved_at = Column(DateTime, nullable=True)
