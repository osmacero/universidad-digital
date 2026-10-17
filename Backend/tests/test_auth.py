from unittest.mock import patch
from uuid import uuid4

import pytest

from app.auth.schemas import TokenResponse
from app.auth.services import (
    create_access_token,
    decode_access_token,
    hash_password,
    password_hasher,
)
from app.core.exceptions import UnauthorizedError


def test_login_success(client):
    with patch("app.auth.routes.authenticate") as mock_authenticate:
        mock_authenticate.return_value = TokenResponse(
            access_token="token-de-prueba"
        )

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "usuario@universidaddigital.com",
                "password": "clave-correcta",
            },
        )

    assert response.status_code == 200
    assert response.json()["access_token"] == "token-de-prueba"
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    with patch("app.auth.routes.authenticate") as mock_authenticate:
        mock_authenticate.side_effect = UnauthorizedError(
            "Invalid email or password"
        )

        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "usuario@universidaddigital.com",
                "password": "clave-incorrecta",
            },
        )

    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code in (401, 403)


def test_hash_password():
    password = "ClaveSegura123!"

    hashed = hash_password(password)

    assert hashed != password
    assert password_hasher.verify(password, hashed)


def test_create_and_decode_access_token():
    user_id = uuid4()

    token = create_access_token(user_id)
    decoded_user_id = decode_access_token(token)

    assert decoded_user_id == user_id


def test_decode_invalid_token():
    with pytest.raises(UnauthorizedError):
        decode_access_token("token-invalido")