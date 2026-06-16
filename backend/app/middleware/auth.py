from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.config import settings
from app.database import set_current_org, get_default_org
from app.routers.auth import decode_jwt

EXEMPT_PATHS = {"/api/health", "/api/auth/login", "/api/auth/register", "/api/auth/forgot-password", "/api/auth/reset-password", "/api/subscription/plans", "/", "/deals/new", "/login", "/api/docs", "/api/redoc", "/openapi.json"}


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        org_id = request.headers.get("X-Organization-ID") or get_default_org()
        if org_id:
            set_current_org(org_id)

        path = request.url.path
        if path in EXEMPT_PATHS or path.startswith("/static") or path.startswith("/web/"):
            return await call_next(request)

        if not path.startswith("/api/"):
            return await call_next(request)

        if not settings.auth_enabled:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        api_key = request.headers.get("X-API-Key") or request.query_params.get("api_key")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_jwt(token)
            if payload:
                org_id = payload.get("org")
                set_current_org(org_id)
                request.state.user_id = payload.get("sub")
                request.state.user_role = payload.get("role")
                request.state.org_id = org_id
                return await call_next(request)
            return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

        if api_key and api_key == settings.api_key:
            return await call_next(request)

        return JSONResponse(status_code=401, content={"detail": "Authentication required"})
