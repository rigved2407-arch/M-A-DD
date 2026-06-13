from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DealCreate(BaseModel):
    deal_name: str
    target_company: str
    acquirer: Optional[str] = ""
    deal_type: Optional[str] = "M&A"
    description: Optional[str] = None
    client_id: Optional[str] = None


class DealOut(BaseModel):
    id: str
    deal_name: str
    target_company: str
    acquirer: Optional[str] = ""
    deal_type: str
    description: Optional[str] = None
    status: str
    document_count: int
    issue_count: int
    risk_score: Optional[float] = None
    client_id: Optional[str] = None
    assigned_to: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    id: str
    deal_id: str
    filename: str
    file_type: Optional[str] = None
    file_size: int = 0
    workstream: str = "other"
    status: str
    summary: Optional[str] = None
    extracted_data: Optional[dict] = None
    red_flags: Optional[list] = None
    created_at: datetime

    class Config:
        from_attributes = True


class IssueCreate(BaseModel):
    document_id: Optional[str] = None
    workstream: Optional[str] = None
    title: str
    description: Optional[str] = None
    severity: str = "medium"
    category: Optional[str] = None
    reference_text: Optional[str] = None
    recommendation: Optional[str] = None
    assignee: Optional[str] = None


class IssueOut(BaseModel):
    id: str
    deal_id: str
    document_id: Optional[str] = None
    workstream: Optional[str] = None
    title: str
    description: Optional[str] = None
    severity: str
    status: str
    category: Optional[str] = None
    reference_text: Optional[str] = None
    recommendation: Optional[str] = None
    assignee: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QAResponse(BaseModel):
    question: str
    answer: str
    citations: list[dict] = []


class ReportOut(BaseModel):
    id: str
    deal_id: str
    status: str
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    name: str
    role: str = "associate"
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None


class ClientOut(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DealActivityOut(BaseModel):
    id: str
    deal_id: str
    user_id: Optional[str] = None
    action: str
    details: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
