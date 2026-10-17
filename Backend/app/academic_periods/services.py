"""Academic period business operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.academic_periods.models import AcademicPeriod
from app.academic_periods.schemas import AcademicPeriodCreate, AcademicPeriodUpdate
from app.core.exceptions import ConflictError, NotFoundError


def get_academic_period(db: Session, period_id: UUID) -> AcademicPeriod:
    period = db.get(AcademicPeriod, period_id)
    if period is None:
        raise NotFoundError("Academic period not found")
    return period


def list_academic_periods(db: Session, offset: int, limit: int) -> list[AcademicPeriod]:
    statement = select(AcademicPeriod).order_by(AcademicPeriod.start_date.desc()).offset(offset).limit(limit)
    return list(db.scalars(statement).all())


def create_academic_period(db: Session, payload: AcademicPeriodCreate) -> AcademicPeriod:
    period = AcademicPeriod(**payload.model_dump())
    db.add(period)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("An academic period with this name already exists") from exc
    db.refresh(period)
    return period


def update_academic_period(
    db: Session, period_id: UUID, payload: AcademicPeriodUpdate
) -> AcademicPeriod:
    period = get_academic_period(db, period_id)
    for field, value in payload.model_dump().items():
        setattr(period, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("An academic period with this name already exists") from exc
    db.refresh(period)
    return period


def deactivate_academic_period(db: Session, period_id: UUID) -> None:
    period = get_academic_period(db, period_id)
    period.is_active = False
    db.commit()
