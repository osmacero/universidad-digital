"""Academic period schemas."""

from datetime import date, datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AcademicPeriodBase(BaseModel):
    """Shared validated period fields."""

    name: str = Field(min_length=2, max_length=80)
    start_date: date
    end_date: date
    enrollment_start: date
    enrollment_end: date

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        if self.enrollment_end < self.enrollment_start:
            raise ValueError("enrollment_end must be on or after enrollment_start")
        if self.enrollment_start > self.end_date or self.enrollment_end < self.start_date:
            raise ValueError("enrollment window must overlap the academic period")
        return self


class AcademicPeriodCreate(AcademicPeriodBase):
    """Data required to create an academic period."""


class AcademicPeriodUpdate(BaseModel):
    """Complete replacement fields for an academic period."""

    name: str = Field(min_length=2, max_length=80)
    start_date: date
    end_date: date
    enrollment_start: date
    enrollment_end: date
    is_active: bool

    @model_validator(mode="after")
    def validate_dates(self) -> Self:
        AcademicPeriodBase.model_validate(self.model_dump(exclude={"is_active"}))
        return self


class AcademicPeriodResponse(AcademicPeriodBase):
    """Public academic period representation."""

    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
