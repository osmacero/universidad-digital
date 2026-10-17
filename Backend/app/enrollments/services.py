"""Student enrollment business operations."""

from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.academic_periods.models import AcademicPeriod
from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError
from app.enrollments.models import Enrollment, EnrollmentStatus
from app.enrollments.schemas import EnrollmentCreate, EnrollmentUpdate
from app.subjects.models import Subject
from app.users.models import User


def _is_admin(user: User) -> bool:
    return "administrator" in {role.name for role in user.roles}


def get_enrollment(db: Session, enrollment_id: UUID, actor: User) -> Enrollment:
    enrollment = db.get(Enrollment, enrollment_id)
    if enrollment is None or (not _is_admin(actor) and enrollment.student_id != actor.id):
        raise NotFoundError("Enrollment not found")
    return enrollment


def list_enrollments(db: Session, offset: int, limit: int, actor: User) -> list[Enrollment]:
    statement = select(Enrollment)
    if not _is_admin(actor):
        statement = statement.where(Enrollment.student_id == actor.id)
    return list(db.scalars(statement.order_by(Enrollment.created_at).offset(offset).limit(limit)).all())


def create_enrollment(db: Session, payload: EnrollmentCreate, actor: User) -> Enrollment:
    if not _is_admin(actor) and payload.student_id != actor.id:
        raise ForbiddenError("Students may only enroll themselves")
    student = db.get(User, payload.student_id)
    if student is None or not student.is_active or "student" not in {role.name for role in student.roles}:
        raise NotFoundError("Active student not found")
    subject = db.get(Subject, payload.subject_id)
    if subject is None or not subject.is_active:
        raise NotFoundError("Active subject not found")
    period = db.get(AcademicPeriod, payload.academic_period_id)
    if period is None or not period.is_active:
        raise NotFoundError("Active academic period not found")
    today = date.today()
    if not period.enrollment_start <= today <= period.enrollment_end:
        raise ConflictError("Enrollment window is closed")
    enrollment = Enrollment(**payload.model_dump())
    db.add(enrollment)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("Student is already enrolled in this subject and period") from exc
    db.refresh(enrollment)
    return enrollment


def update_enrollment(db: Session, enrollment_id: UUID, payload: EnrollmentUpdate, actor: User) -> Enrollment:
    if not _is_admin(actor):
        raise ForbiddenError("Only administrators may set enrollment state")
    enrollment = get_enrollment(db, enrollment_id, actor)
    if enrollment.status == EnrollmentStatus.COMPLETED:
        raise ConflictError("A completed enrollment cannot change state")
    enrollment.status = payload.status
    db.commit()
    db.refresh(enrollment)
    return enrollment


def cancel_enrollment(db: Session, enrollment_id: UUID, actor: User) -> None:
    enrollment = get_enrollment(db, enrollment_id, actor)
    if enrollment.status == EnrollmentStatus.COMPLETED:
        raise ConflictError("A completed enrollment cannot be cancelled")
    enrollment.status = EnrollmentStatus.CANCELLED
    db.commit()
