"""Academic grade ORM model."""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models import TimestampMixin, UUIDPrimaryKeyMixin


class Grade(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Named assessment grade attached to an enrollment."""

    __tablename__ = "grades"
    __table_args__ = (
        CheckConstraint("score >= 0 AND score <= 5", name="ck_grade_score_range"),
        CheckConstraint("weight > 0 AND weight <= 100", name="ck_grade_weight_range"),
    )

    enrollment_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("enrollments.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(3, 2), nullable=False)
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    observations: Mapped[str | None] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enrollment: Mapped[Enrollment] = relationship(back_populates="grades")


if TYPE_CHECKING:
    from app.enrollments.models import Enrollment
