"""Academic period ORM model."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models import TimestampMixin, UUIDPrimaryKeyMixin


class AcademicPeriod(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Date-bounded academic period."""

    __tablename__ = "academic_periods"
    __table_args__ = (CheckConstraint("end_date >= start_date", name="ck_period_date_order"),)

    name: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    enrollment_start: Mapped[date] = mapped_column(Date, nullable=False)
    enrollment_end: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enrollments: Mapped[list[Enrollment]] = relationship(back_populates="academic_period")


if TYPE_CHECKING:
    from app.enrollments.models import Enrollment
