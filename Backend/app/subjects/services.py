"""Academic subject business operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.subjects.models import Subject
from app.subjects.schemas import SubjectCreate, SubjectUpdate
from app.users.models import User


def _validate_teacher(db: Session, teacher_id: UUID | None) -> None:
    if teacher_id is None:
        return
    teacher = db.get(User, teacher_id)
    if teacher is None or not teacher.is_active or "teacher" not in {role.name for role in teacher.roles}:
        raise NotFoundError("Active teacher not found")


def get_subject(db: Session, subject_id: UUID) -> Subject:
    subject = db.get(Subject, subject_id)
    if subject is None:
        raise NotFoundError("Subject not found")
    return subject


def list_subjects(db: Session, offset: int, limit: int) -> list[Subject]:
    return list(db.scalars(select(Subject).order_by(Subject.code).offset(offset).limit(limit)).all())


def create_subject(db: Session, payload: SubjectCreate) -> Subject:
    _validate_teacher(db, payload.teacher_id)
    subject = Subject(**payload.model_dump())
    db.add(subject)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A subject with this code already exists") from exc
    db.refresh(subject)
    return subject


def update_subject(db: Session, subject_id: UUID, payload: SubjectUpdate) -> Subject:
    subject = get_subject(db, subject_id)
    changes = payload.model_dump(exclude_unset=True)
    if "teacher_id" in changes:
        _validate_teacher(db, changes["teacher_id"])
    for field, value in changes.items():
        setattr(subject, field, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A subject with this code already exists") from exc
    db.refresh(subject)
    return subject


def deactivate_subject(db: Session, subject_id: UUID) -> None:
    subject = get_subject(db, subject_id)
    subject.is_active = False
    db.commit()
