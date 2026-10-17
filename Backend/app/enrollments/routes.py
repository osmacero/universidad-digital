"""Student enrollment HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import CurrentUser, DatabaseSession, require_roles
from app.core.pagination import Limit, Offset
from app.enrollments.models import Enrollment
from app.enrollments.schemas import EnrollmentCreate, EnrollmentResponse, EnrollmentUpdate
from app.enrollments.services import (
    cancel_enrollment,
    create_enrollment,
    get_enrollment,
    list_enrollments,
    update_enrollment,
)
from app.users.models import User

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create(payload: EnrollmentCreate, db: DatabaseSession, current_user: CurrentUser) -> Enrollment:
    return create_enrollment(db, payload, current_user)


@router.get("/", response_model=list[EnrollmentResponse])
def list_all(
    db: DatabaseSession, current_user: CurrentUser, offset: Offset = 0, limit: Limit = 50
) -> list[Enrollment]:
    return list_enrollments(db, offset, limit, current_user)


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
def retrieve(enrollment_id: UUID, db: DatabaseSession, current_user: CurrentUser) -> Enrollment:
    return get_enrollment(db, enrollment_id, current_user)


@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
def update(
    enrollment_id: UUID,
    payload: EnrollmentUpdate,
    db: DatabaseSession,
    current_user: User = Depends(require_roles("administrator")),
) -> Enrollment:
    return update_enrollment(db, enrollment_id, payload, current_user)


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(enrollment_id: UUID, db: DatabaseSession, current_user: CurrentUser) -> Response:
    cancel_enrollment(db, enrollment_id, current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
