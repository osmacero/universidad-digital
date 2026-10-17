"""Academic subject HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import CurrentUser, DatabaseSession, require_roles
from app.core.pagination import Limit, Offset
from app.subjects.models import Subject
from app.subjects.schemas import SubjectCreate, SubjectResponse, SubjectUpdate
from app.subjects.services import create_subject, deactivate_subject, get_subject, list_subjects, update_subject
from app.users.models import User

router = APIRouter(prefix="/subjects", tags=["subjects"])


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: SubjectCreate,
    db: DatabaseSession,
    _: User = Depends(require_roles("administrator")),
) -> Subject:
    return create_subject(db, payload)


@router.get("/", response_model=list[SubjectResponse])
def list_all(_: CurrentUser, db: DatabaseSession, offset: Offset = 0, limit: Limit = 50) -> list[Subject]:
    return list_subjects(db, offset, limit)


@router.get("/{subject_id}", response_model=SubjectResponse)
def retrieve(subject_id: UUID, _: CurrentUser, db: DatabaseSession) -> Subject:
    return get_subject(db, subject_id)


@router.put("/{subject_id}", response_model=SubjectResponse)
def update(
    subject_id: UUID,
    payload: SubjectUpdate,
    db: DatabaseSession,
    _: User = Depends(require_roles("administrator")),
) -> Subject:
    return update_subject(db, subject_id, payload)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    subject_id: UUID,
    db: DatabaseSession,
    _: User = Depends(require_roles("administrator")),
) -> Response:
    deactivate_subject(db, subject_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
