"""Academic subject schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubjectCreate(BaseModel):
    """Data required to create a subject."""

    code: str = Field(min_length=2, max_length=20, pattern=r"^[A-Za-z0-9_-]+$")
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    credits: int = Field(ge=1, le=30)
    teacher_id: UUID | None = None

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.upper()


class SubjectUpdate(BaseModel):
    """Mutable subject fields."""

    code: str | None = Field(default=None, min_length=2, max_length=20, pattern=r"^[A-Za-z0-9_-]+$")
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)
    credits: int | None = Field(default=None, ge=1, le=30)
    teacher_id: UUID | None = None
    is_active: bool | None = None

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        return value.upper() if value else value


class SubjectResponse(BaseModel):
    """Public subject representation."""

    id: UUID
    code: str
    name: str
    description: str | None
    credits: int
    teacher_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
