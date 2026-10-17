"""Authentication HTTP endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.auth.dependencies import CurrentUser, DatabaseSession
from app.auth.schemas import LoginRequest, TokenResponse
from app.auth.services import authenticate
from app.users.schemas import UserResponse

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, db: DatabaseSession) -> TokenResponse:
    """Authenticate a user and return a bearer token."""

    return authenticate(db, payload)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: CurrentUser) -> UserResponse:
    """Return the authenticated user's safe profile."""

    return UserResponse.model_validate(current_user)
