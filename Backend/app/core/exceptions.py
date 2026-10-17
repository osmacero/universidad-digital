"""Controlled application exceptions."""


class ApplicationError(Exception):
    """Base error that can be safely translated to an HTTP response."""

    status_code: int = 400

    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.detail = detail


class NotFoundError(ApplicationError):
    """Requested resource does not exist."""

    status_code = 404


class ConflictError(ApplicationError):
    """Operation conflicts with existing state."""

    status_code = 409


class UnauthorizedError(ApplicationError):
    """Authentication credentials are invalid."""

    status_code = 401


class ForbiddenError(ApplicationError):
    """Authenticated principal lacks permission."""

    status_code = 403
