"""Academic grade HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import CurrentUser, DatabaseSession, require_roles
from app.core.pagination import Limit, Offset
from app.grades.models import Grade
from app.grades.schemas import GradeCreate, GradeResponse, GradeUpdate
from app.grades.services import create_grade, deactivate_grade, get_grade, list_grades, update_grade
from app.users.models import User

router = APIRouter(prefix="/grades", tags=["grades"])


@router.post("/", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: GradeCreate,
    db: DatabaseSession,
    current_user: User = Depends(require_roles("administrator", "teacher")),
) -> Grade:
    return create_grade(db, payload, current_user)


@router.get("/", response_model=list[GradeResponse])
def list_all(
    db: DatabaseSession, current_user: CurrentUser, offset: Offset = 0, limit: Limit = 50
) -> list[Grade]:
    return list_grades(db, offset, limit, current_user)


@router.get("/{grade_id}", response_model=GradeResponse)
def retrieve(grade_id: UUID, db: DatabaseSession, current_user: CurrentUser) -> Grade:
    return get_grade(db, grade_id, current_user)


@router.put("/{grade_id}", response_model=GradeResponse)
def update(
    grade_id: UUID,
    payload: GradeUpdate,
    db: DatabaseSession,
    current_user: User = Depends(require_roles("administrator", "teacher")),
) -> Grade:
    return update_grade(db, grade_id, payload, current_user)


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    grade_id: UUID,
    db: DatabaseSession,
    current_user: User = Depends(require_roles("administrator", "teacher")),
) -> Response:
    deactivate_grade(db, grade_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
