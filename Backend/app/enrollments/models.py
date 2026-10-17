"""Student enrollment ORM model."""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models import TimestampMixin, UUIDPrimaryKeyMixin


class EnrollmentStatus(StrEnum):
    """Allowed enrollment lifecycle states."""

    ACTIVE = "active"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Enrollment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A student's enrollment in one subject and period."""

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", "academic_period_id", name="uq_enrollment_context"),
    )

    student_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    subject_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("subjects.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    academic_period_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("academic_periods.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus, name="enrollment_status"), default=EnrollmentStatus.ACTIVE, nullable=False
    )
    student: Mapped[User] = relationship(back_populates="enrollments")
    subject: Mapped[Subject] = relationship(back_populates="enrollments")
    academic_period: Mapped[AcademicPeriod] = relationship(back_populates="enrollments")
    grades: Mapped[list[Grade]] = relationship(back_populates="enrollment")


if TYPE_CHECKING:
    from app.academic_periods.models import AcademicPeriod
    from app.grades.models import Grade
    from app.subjects.models import Subject
    from app.users.models import User
