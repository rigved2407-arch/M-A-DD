import uuid
from sqlalchemy.orm import Session

from app.database import disable_tenant_filter, enable_tenant_filter
from app.models import Organization


def get_or_create_default_org(db: Session) -> Organization:
    disable_tenant_filter()
    try:
        org = db.query(Organization).filter(Organization.name == "Default Organization").first()
        if not org:
            org = Organization(
                id=str(uuid.uuid4()),
                name="Default Organization",
                email="admin@default.local",
            )
            db.add(org)
            db.commit()
            db.refresh(org)
        return org
    finally:
        enable_tenant_filter()
