import traceback
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("ma_dd.error_handler")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error("Unhandled error: %s\n%s", exc, traceback.format_exc())
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "message": str(exc) if request.app.debug else "An unexpected error occurred"},
            )
