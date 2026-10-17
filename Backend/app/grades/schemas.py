"""Academic grade schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GradeCreate(BaseModel):
    """Data required to register a grade."""

    enrollment_id: UUID
    name: str = Field(min_length=1, max_length=100)
    score: Decimal = Field(ge=Decimal("0"), le=Decimal("5"), decimal_places=2)
    weight: Decimal = Field(gt=Decimal("0"), le=Decimal("100"), decimal_places=2)
    observations: str | None = Field(default=None, max_length=500)


class GradeUpdate(BaseModel):
    """Mutable grade fields."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    score: Decimal | None = Field(default=None, ge=Decimal("0"), le=Decimal("5"), decimal_places=2)
    weight: Decimal | None = Field(default=None, gt=Decimal("0"), le=Decimal("100"), decimal_places=2)
    observations: str | None = Field(default=None, max_length=500)


class GradeResponse(BaseModel):
    """Public grade representation."""

    id: UUID
    enrollment_id: UUID
    name: str
    score: Decimal
    weight: Decimal
    observations: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
