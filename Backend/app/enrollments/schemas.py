"""Student enrollment schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.enrollments.models import EnrollmentStatus


class EnrollmentCreate(BaseModel):
    """References required to enroll a student."""

    student_id: UUID
    subject_id: UUID
    academic_period_id: UUID


class EnrollmentUpdate(BaseModel):
    """Allowed enrollment state transition request."""

    status: EnrollmentStatus


class EnrollmentResponse(BaseModel):
    """Public enrollment representation."""

    id: UUID
    student_id: UUID
    subject_id: UUID
    academic_period_id: UUID
    status: EnrollmentStatus
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
