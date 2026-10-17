"""User and role request/response schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RoleResponse(BaseModel):
    """Public role representation."""

    id: UUID
    name: str
    description: str | None
    model_config = ConfigDict(from_attributes=True)


class RoleCreate(BaseModel):
    """Data required to create an authorization role."""

    name: str = Field(min_length=2, max_length=50, pattern=r"^[a-z][a-z0-9_-]+$")
    description: str | None = Field(default=None, max_length=255)


class RoleUpdate(BaseModel):
    """Mutable authorization role fields."""

    name: str | None = Field(default=None, min_length=2, max_length=50, pattern=r"^[a-z][a-z0-9_-]+$")
    description: str | None = Field(default=None, max_length=255)


class UserCreate(BaseModel):
    """Data required to create a user."""

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=12, max_length=128)
    role_ids: set[UUID] = Field(default_factory=set)


class UserUpdate(BaseModel):
    """Mutable user fields."""

    email: EmailStr | None = None
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    password: str | None = Field(default=None, min_length=12, max_length=128)
    role_ids: set[UUID] | None = None
    is_active: bool | None = None


class UserResponse(BaseModel):
    """Safe user representation without password data."""

    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool
    roles: list[RoleResponse]
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
