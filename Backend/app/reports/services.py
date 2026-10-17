"""Read-only academic report operations."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError, NotFoundError
from app.enrollments.models import Enrollment
from app.grades.models import Grade
from app.reports.schemas import StudentAcademicReport, SubjectResult
from app.subjects.models import Subject
from app.users.models import User


def build_student_report(db: Session, student_id: UUID, actor: User) -> StudentAcademicReport:
    """Compute a student's accumulated scores without exposing unrelated records."""

    if "administrator" not in {role.name for role in actor.roles} and actor.id != student_id:
        raise ForbiddenError("Students may only access their own report")
    student = db.get(User, student_id)
    if student is None or "student" not in {role.name for role in student.roles}:
        raise NotFoundError("Student not found")
    statement = (
        select(
            Enrollment.id,
            Subject.code,
            Subject.name,
            func.coalesce(func.sum(Grade.score * Grade.weight / 100), 0),
            func.coalesce(func.sum(Grade.weight), 0),
        )
        .join(Subject, Enrollment.subject_id == Subject.id)
        .outerjoin(Grade, (Grade.enrollment_id == Enrollment.id) & Grade.is_active.is_(True))
        .where(Enrollment.student_id == student_id)
        .group_by(Enrollment.id, Subject.code, Subject.name)
        .order_by(Subject.code)
    )
    results = [
        SubjectResult(
            enrollment_id=row[0],
            subject_code=row[1],
            subject_name=row[2],
            accumulated_score=Decimal(row[3]),
            graded_weight=Decimal(row[4]),
        )
        for row in db.execute(statement)
    ]
    return StudentAcademicReport(student_id=student.id, student_name=student.full_name, results=results)
