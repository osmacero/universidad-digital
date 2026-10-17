"""Academic period HTTP endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.academic_periods.models import AcademicPeriod
from app.academic_periods.schemas import AcademicPeriodCreate, AcademicPeriodResponse, AcademicPeriodUpdate
from app.academic_periods.services import (
    create_academic_period,
    deactivate_academic_period,
    get_academic_period,
    list_academic_periods,
    update_academic_period,
)
from app.auth.dependencies import CurrentUser, DatabaseSession, require_roles
from app.core.pagination import Limit, Offset
from app.users.models import User

router = APIRouter(prefix="/academic-periods", tags=["academic periods"])


@router.post("/", response_model=AcademicPeriodResponse, status_code=status.HTTP_201_CREATED)
def create(
    payload: AcademicPeriodCreate,
    db: DatabaseSession,
    _: User = Depends(require_roles("administrator")),
) -> AcademicPeriod:
    return create_academic_period(db, payload)


@router.get("/", response_model=list[AcademicPeriodResponse])
def list_all(_: CurrentUser, db: DatabaseSession, offset: Offset = 0, limit: Limit = 50) -> list[AcademicPeriod]:
    return list_academic_periods(db, offset, limit)


@router.get("/{period_id}", response_model=AcademicPeriodResponse)
def retrieve(period_id: UUID, _: CurrentUser, db: DatabaseSession) -> AcademicPeriod:
    return get_academic_period(db, period_id)


@router.put("/{period_id}", response_model=AcademicPeriodResponse)
def update(
    period_id: UUID,
    payload: AcademicPeriodUpdate,
    db: DatabaseSession,
    _: User = Depends(require_roles("administrator")),
) -> AcademicPeriod:
    return update_academic_period(db, period_id, payload)


@router.delete("/{period_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(
    period_id: UUID,
    db: DatabaseSession,
    _: User = Depends(require_roles("administrator")),
) -> Response:
    deactivate_academic_period(db, period_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
