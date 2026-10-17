"""User business operations."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.services import hash_password
from app.core.exceptions import ConflictError, NotFoundError
from app.users.models import Role, User
from app.users.schemas import RoleCreate, RoleUpdate, UserCreate, UserUpdate

SYSTEM_ROLES = frozenset({"administrator", "teacher", "student"})


def _get_roles(db: Session, role_ids: set[UUID]) -> list[Role]:
    roles = list(db.scalars(select(Role).where(Role.id.in_(role_ids))).all()) if role_ids else []
    if len(roles) != len(role_ids):
        raise NotFoundError("One or more roles do not exist")
    return roles


def get_user(db: Session, user_id: UUID) -> User:
    """Return a user or raise a controlled not-found error."""

    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("User not found")
    return user


def list_users(db: Session, offset: int, limit: int) -> list[User]:
    """Return a bounded page of users."""

    return list(db.scalars(select(User).order_by(User.created_at).offset(offset).limit(limit)).all())


def create_user(db: Session, payload: UserCreate) -> User:
    """Create a user and atomically assign existing roles."""

    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name.strip(),
        password_hash=hash_password(payload.password),
        roles=_get_roles(db, payload.role_ids),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A user with this email already exists") from exc
    db.refresh(user)
    return user


def update_user(db: Session, user_id: UUID, payload: UserUpdate) -> User:
    """Update supplied user fields in one transaction."""

    user = get_user(db, user_id)
    changes = payload.model_dump(exclude_unset=True)
    role_ids = changes.pop("role_ids", None)
    password = changes.pop("password", None)
    if "email" in changes:
        changes["email"] = changes["email"].lower()
    if "full_name" in changes:
        changes["full_name"] = changes["full_name"].strip()
    for field, value in changes.items():
        setattr(user, field, value)
    if password is not None:
        user.password_hash = hash_password(password)
    if role_ids is not None:
        user.roles = _get_roles(db, role_ids)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A user with this email already exists") from exc
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: UUID) -> None:
    """Logically delete a user while preserving academic history."""

    user = get_user(db, user_id)
    user.is_active = False
    db.commit()


def get_role(db: Session, role_id: UUID) -> Role:
    """Return a role or raise a controlled not-found error."""

    role = db.get(Role, role_id)
    if role is None:
        raise NotFoundError("Role not found")
    return role


def list_roles(db: Session) -> list[Role]:
    """Return all roles in stable name order."""

    return list(db.scalars(select(Role).order_by(Role.name)).all())


def create_role(db: Session, payload: RoleCreate) -> Role:
    """Create a role with a unique normalized name."""

    role = Role(name=payload.name.lower(), description=payload.description)
    db.add(role)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A role with this name already exists") from exc
    db.refresh(role)
    return role


def update_role(db: Session, role_id: UUID, payload: RoleUpdate) -> Role:
    """Update a non-system role."""

    role = get_role(db, role_id)
    if role.name in SYSTEM_ROLES:
        raise ConflictError("System roles cannot be modified")
    changes = payload.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(role, field, value.lower() if field == "name" else value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise ConflictError("A role with this name already exists") from exc
    db.refresh(role)
    return role


def delete_role(db: Session, role_id: UUID) -> None:
    """Delete an unused, non-system role."""

    role = get_role(db, role_id)
    if role.name in SYSTEM_ROLES or role.users:
        raise ConflictError("System roles and assigned roles cannot be deleted")
    db.delete(role)
    db.commit()
