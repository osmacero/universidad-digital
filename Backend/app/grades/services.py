"""Academic grade business operations."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.enrollments.models import Enrollment, EnrollmentStatus
from app.grades.models import Grade
from app.grades.schemas import GradeCreate, GradeUpdate
from app.subjects.models import Subject
from app.users.models import User


def _role_names(user: User) -> set[str]:
    return {role.name for role in user.roles}


def _grade_scope(actor: User):
    statement = select(Grade).join(Enrollment, Grade.enrollment_id == Enrollment.id)
    roles = _role_names(actor)
    if "administrator" in roles:
        return statement
    if "teacher" in roles:
        return statement.join(Subject, Enrollment.subject_id == Subject.id).where(Subject.teacher_id == actor.id)
    return statement.where(Enrollment.student_id == actor.id)


def get_grade(db: Session, grade_id: UUID, actor: User) -> Grade:
    grade = db.scalar(_grade_scope(actor).where(Grade.id == grade_id, Grade.is_active.is_(True)))
    if grade is None:
        raise NotFoundError("Grade not found")
    return grade


def list_grades(db: Session, offset: int, limit: int, actor: User) -> list[Grade]:
    statement = _grade_scope(actor).where(Grade.is_active.is_(True)).order_by(Grade.created_at).offset(offset).limit(limit)
    return list(db.scalars(statement).all())


def _validate_weight(db: Session, enrollment_id: UUID, weight: Decimal, exclude_id: UUID | None = None) -> None:
    statement = select(func.coalesce(func.sum(Grade.weight), 0)).where(
        Grade.enrollment_id == enrollment_id, Grade.is_active.is_(True)
    )
    if exclude_id is not None:
        statement = statement.where(Grade.id != exclude_id)
    current_weight = Decimal(db.scalar(statement) or 0)
    if current_weight + weight > Decimal("100"):
        raise ConflictError("Total active grade weight cannot exceed 100 percent")


def create_grade(db: Session, payload: GradeCreate, actor: User) -> Grade:
    enrollment = db.get(Enrollment, payload.enrollment_id)
    if enrollment is None or enrollment.status != EnrollmentStatus.ACTIVE:
        raise NotFoundError("Active enrollment not found")
    if "administrator" not in _role_names(actor):
        subject = db.get(Subject, enrollment.subject_id)
        if subject is None or subject.teacher_id != actor.id:
            raise NotFoundError("Assigned active enrollment not found")
    _validate_weight(db, payload.enrollment_id, payload.weight)
    grade = Grade(**payload.model_dump())
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


def update_grade(db: Session, grade_id: UUID, payload: GradeUpdate, actor: User) -> Grade:
    grade = get_grade(db, grade_id, actor)
    changes = payload.model_dump(exclude_unset=True)
    _validate_weight(db, grade.enrollment_id, changes.get("weight", grade.weight), grade.id)
    for field, value in changes.items():
        setattr(grade, field, value)
    db.commit()
    db.refresh(grade)
    return grade


def deactivate_grade(db: Session, grade_id: UUID, actor: User) -> None:
    grade = get_grade(db, grade_id, actor)
    grade.is_active = False
    db.commit()
