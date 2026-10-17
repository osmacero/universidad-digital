"""Academic report HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.auth.dependencies import CurrentUser, DatabaseSession
from app.reports.schemas import StudentAcademicReport
from app.reports.services import build_student_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/students/{student_id}", response_model=StudentAcademicReport)
def student_report(student_id: UUID, db: DatabaseSession, current_user: CurrentUser) -> StudentAcademicReport:
    """Return a basic accumulated-grade report for an authorized student."""

    return build_student_report(db, student_id, current_user)
