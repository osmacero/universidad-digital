"""Academic report response schemas."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field


class SubjectResult(BaseModel):
    """Computed result for one enrolled subject."""

    enrollment_id: UUID
    subject_code: str
    subject_name: str
    accumulated_score: Decimal = Field(ge=Decimal("0"), le=Decimal("5"))
    graded_weight: Decimal = Field(ge=Decimal("0"), le=Decimal("100"))


class StudentAcademicReport(BaseModel):
    """Basic academic report for one student."""

    student_id: UUID
    student_name: str
    results: list[SubjectResult]
