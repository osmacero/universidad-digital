"""Centralized exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import ApplicationError


async def application_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """Return a stable error envelope for controlled application errors."""

    error = exc if isinstance(exc, ApplicationError) else ApplicationError("Unexpected error")
    return JSONResponse(status_code=error.status_code, content={"detail": error.detail})


def register_error_handlers(app: FastAPI) -> None:
    """Register application-level exception mappings."""

    app.add_exception_handler(ApplicationError, application_error_handler)
