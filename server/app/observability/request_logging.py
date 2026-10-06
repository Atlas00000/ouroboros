"""HTTP request logging middleware — request_id + duration JSON lines."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.observability.logging import clear_request_context, set_request_context

logger = logging.getLogger("ouroboros.http")

REQUEST_ID_HEADER = "X-Request-Id"

# Skip high-chatter / probe paths from info logs (still get errors).
_SKIP_INFO_PATHS = frozenset(
    {
        "/metrics",
        "/favicon.ico",
        "/json/version",
        "/json/list",
    }
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Assign/propagate request id, log method/path/status/duration_ms."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        incoming = request.headers.get(REQUEST_ID_HEADER)
        request_id = (incoming or "").strip() or str(uuid.uuid4())
        path = request.url.path
        set_request_context(request_id=request_id, path=path)
        request.state.request_id = request_id

        started = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        except Exception:
            logger.exception(
                "http_unhandled",
                extra={
                    "method": request.method,
                    "path": path,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            skip_info = path in _SKIP_INFO_PATHS or path.startswith("/_next")
            level = logging.DEBUG if skip_info and status < 400 else logging.INFO
            if status >= 500:
                level = logging.ERROR
            elif status >= 400:
                level = logging.WARNING
            logger.log(
                level,
                "http_request",
                extra={
                    "method": request.method,
                    "path": path,
                    "status": status,
                    "duration_ms": duration_ms,
                    "client": request.client.host if request.client else None,
                },
            )
            clear_request_context()
