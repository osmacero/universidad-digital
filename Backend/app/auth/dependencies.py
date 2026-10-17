"""Reusable FastAPI authentication and role dependencies."""

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.services import decode_access_token
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.users.models import User

bearer_scheme = HTTPBearer()
DatabaseSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DatabaseSession,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    ) -> User:
    """Resolve the active user represented by a bearer token."""

    token = credentials.credentials
    user = db.get(User, decode_access_token(token))

    if user is None or not user.is_active:
        raise UnauthorizedError("User is inactive or no longer exists")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_roles(*allowed_roles: str) -> Callable[[CurrentUser], User]:
    """Build a dependency enforcing at least one allowed role."""

    def role_checker(user: CurrentUser) -> User:
        if not {role.name for role in user.roles}.intersection(allowed_roles):
            raise ForbiddenError("Insufficient permissions")
        return user

    return role_checker
