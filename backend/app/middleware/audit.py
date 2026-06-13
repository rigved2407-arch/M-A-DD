import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.database import SessionLocal
from app.models import AuditLog


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)

        if not request.url.path.startswith("/api/"):
            return response
        if request.url.path == "/api/health":
            return response

        try:
            db = SessionLocal()
            log = AuditLog(
                method=request.method,
                path=str(request.url.path),
                query_params=str(request.url.query),
                status_code=response.status_code,
                duration_ms=duration_ms,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
            )
            db.add(log)
            db.commit()
            db.close()
        except Exception:
            pass

        return response
