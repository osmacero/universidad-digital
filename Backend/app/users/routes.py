"""User HTTP endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.auth.dependencies import DatabaseSession, require_roles
from app.core.pagination import Limit, Offset
from app.users.models import User
from app.users.models import Role
from app.users.schemas import RoleCreate, RoleResponse, RoleUpdate, UserCreate, UserResponse, UserUpdate
from app.users.services import (
    create_role,
    create_user,
    deactivate_user,
    delete_role,
    get_role,
    get_user,
    list_roles,
    list_users,
    update_role,
    update_user,
)

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(require_roles("administrator"))])
role_router = APIRouter(prefix="/roles", tags=["roles"], dependencies=[Depends(require_roles("administrator"))])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create(payload: UserCreate, db: DatabaseSession) -> User:
    return create_user(db, payload)


@router.get("/", response_model=list[UserResponse])
def list_all(db: DatabaseSession, offset: Offset = 0, limit: Limit = 50) -> list[User]:
    return list_users(db, offset, limit)


@router.get("/{user_id}", response_model=UserResponse)
def retrieve(user_id: UUID, db: DatabaseSession) -> User:
    return get_user(db, user_id)


@router.put("/{user_id}", response_model=UserResponse)
def update(user_id: UUID, payload: UserUpdate, db: DatabaseSession) -> User:
    return update_user(db, user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(user_id: UUID, db: DatabaseSession) -> Response:
    deactivate_user(db, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@role_router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role_endpoint(payload: RoleCreate, db: DatabaseSession) -> Role:
    return create_role(db, payload)


@role_router.get("/", response_model=list[RoleResponse])
def list_role_endpoints(db: DatabaseSession) -> list[Role]:
    return list_roles(db)


@role_router.get("/{role_id}", response_model=RoleResponse)
def retrieve_role(role_id: UUID, db: DatabaseSession) -> Role:
    return get_role(db, role_id)


@role_router.put("/{role_id}", response_model=RoleResponse)
def update_role_endpoint(role_id: UUID, payload: RoleUpdate, db: DatabaseSession) -> Role:
    return update_role(db, role_id, payload)


@role_router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role_endpoint(role_id: UUID, db: DatabaseSession) -> Response:
    delete_role(db, role_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
