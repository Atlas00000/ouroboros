"""RFC 9457 problem+json error model."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException


class ProblemDetails(BaseModel):
    """RFC 9457 Problem Details for HTTP APIs."""

    type: str = Field(default="about:blank")
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    errors: list[dict[str, Any]] | None = None


class AppError(Exception):
    """Raise from handlers / deps to return problem+json."""

    def __init__(
        self,
        *,
        status: int,
        title: str,
        detail: str | None = None,
        type_: str = "about:blank",
        errors: list[dict[str, Any]] | None = None,
    ) -> None:
        self.status = status
        self.title = title
        self.detail = detail
        self.type_ = type_
        self.errors = errors
        super().__init__(detail or title)


def problem_response(
    *,
    status: int,
    title: str,
    detail: str | None = None,
    type_: str = "about:blank",
    instance: str | None = None,
    errors: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    body = ProblemDetails(
        type=type_,
        title=title,
        status=status,
        detail=detail,
        instance=instance,
        errors=errors,
    )
    return JSONResponse(
        status_code=status,
        content=body.model_dump(exclude_none=True),
        media_type="application/problem+json",
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_request: Request, exc: AppError) -> JSONResponse:
        return problem_response(
            status=exc.status,
            title=exc.title,
            detail=exc.detail,
            type_=exc.type_,
            instance=str(_request.url.path),
            errors=exc.errors,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return problem_response(
            status=exc.status_code,
            title="HTTP Error",
            detail=str(exc.detail) if exc.detail is not None else None,
            instance=str(request.url.path),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return problem_response(
            status=422,
            title="Validation Error",
            detail="Request validation failed",
            type_="https://ouroboros.local/problems/validation",
            instance=str(request.url.path),
            errors=[{"loc": e.get("loc"), "msg": e.get("msg"), "type": e.get("type")} for e in exc.errors()],
        )
