"""Academic subject ORM model."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.models import TimestampMixin, UUIDPrimaryKeyMixin


class Subject(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """University subject offered for enrollment."""

    __tablename__ = "subjects"
    __table_args__ = (CheckConstraint("credits > 0", name="ck_subject_credits_positive"),)

    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    credits: Mapped[int] = mapped_column(nullable=False)
    teacher_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    teacher: Mapped[User | None] = relationship(back_populates="subjects_taught")
    enrollments: Mapped[list[Enrollment]] = relationship(back_populates="subject")


if TYPE_CHECKING:
    from app.enrollments.models import Enrollment
    from app.users.models import User
