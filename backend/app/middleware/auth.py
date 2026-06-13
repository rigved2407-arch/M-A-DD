from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.database import set_current_org, get_default_org

EXEMPT_PATHS = {"/api/health", "/", "/deals/new", "/login"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        org_id = request.headers.get("X-Organization-ID") or get_default_org()
        if org_id:
            set_current_org(org_id)

        if not settings.auth_enabled:
            return await call_next(request)

        path = request.url.path

        if path in EXEMPT_PATHS or path.startswith("/static") or path.startswith("/web/"):
            return await call_next(request)

        if path.startswith("/api/"):
            api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")
            if not api_key or api_key != settings.api_key:
                return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})

        return await call_next(request)
