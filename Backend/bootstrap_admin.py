from getpass import getpass

from sqlalchemy import select

import app.main  # Carga todos los modelos ORM
from app.core.database import SessionLocal
from app.users.models import Role
from app.users.schemas import UserCreate
from app.users.services import create_user


email = input("Email: ").strip()
full_name = input("Nombre completo: ").strip()
password = getpass("Password: ")
confirm = getpass("Confirmar password: ")

if password != confirm:
    raise SystemExit("Las contraseñas no coinciden.")

with SessionLocal() as db:
    role = db.scalar(select(Role).where(Role.name == "administrator"))

    if role is None:
        raise SystemExit("No existe el rol administrator.")

    payload = UserCreate(
        email=email,
        full_name=full_name,
        password=password,
        role_ids={role.id},
    )

    user = create_user(db, payload)
    print(f"ADMIN CREADO: {user.email}")