"""Password and JWT authentication services."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.schemas import LoginRequest, TokenResponse
from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError
from app.users.models import User

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Hash a password with the recommended adaptive algorithm."""

    return password_hasher.hash(password)


def authenticate(db: Session, credentials: LoginRequest) -> TokenResponse:
    """Validate credentials and issue a short-lived access token."""

    user = db.scalar(select(User).where(User.email == credentials.email.lower()))
    if user is None or not user.is_active or not password_hasher.verify(credentials.password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")
    return TokenResponse(access_token=create_access_token(user.id))


def create_access_token(user_id: UUID) -> str:
    """Create a signed JWT for a user."""

    settings = get_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
        "type": "access",
    }
    return jwt.encode(payload, settings.jwt_secret_key.get_secret_value(), algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> UUID:
    """Validate a JWT and return its subject."""

    settings = get_settings()
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "iat", "exp", "type"]},
        )
        if payload["type"] != "access":
            raise UnauthorizedError("Invalid token type")
        return UUID(payload["sub"])
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise UnauthorizedError("Invalid or expired access token") from exc
