from starlette import status

from sgde_api.auth.exceptions import (
    InvalidCredentials,
    UserNotFound,
    EmailTaken,
    UsernameTaken,
    LoginRequired,
    InvalidToken,
)
from sgde_api.tests.conftest import foobar
from sgde_utils.schemas import VALID_USERNAME, VALID_PASSWORD


def test_get_empty_user_table(client):
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_non_existing_user(client):
    response = client.get("/users/foobar")
    assert response.status_code == UserNotFound.STATUS_CODE
    assert response.json()["detail"] == UserNotFound.DETAIL


def test_register(client):
    response = client.post("/auth/register", json=foobar)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"username": "foobar", "email": "foobar@example.com"}


def test_get_populated_user_table(client):
    for i in range(5):
        client.post(
            "/auth/register",
            json={
                "username": f"user{i}",
                "email": f"user{i}@example.com",
                "password": "aaaAAA1!",
            },
        )
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {"username": f"user{i}", "email": f"user{i}@example.com"} for i in range(5)
    ]


def test_register_existing_username(client):
    client.post("/auth/register", json=foobar)
    _foobar = foobar.copy()
    _foobar["email"] = "barfoo@example.com"
    response = client.post("/auth/register", json=_foobar)
    assert response.status_code == UsernameTaken.STATUS_CODE
    assert response.json()["detail"] == UsernameTaken.DETAIL


def test_register_existing_email(client):
    client.post("/auth/register", json=foobar)
    _foobar = foobar.copy()
    _foobar["username"] = "barfoo"
    response = client.post("/auth/register", json=_foobar)
    assert response.status_code == EmailTaken.STATUS_CODE
    assert response.json()["detail"] == EmailTaken.DETAIL


def test_get_existing_user(client):
    client.post("/auth/register", json=foobar)
    response = client.get("/users/foobar")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"username": "foobar", "email": "foobar@example.com"}


def test_malformed_username(client):
    _foobar = foobar.copy()
    _foobar["username"] = "foo bar"
    response = client.post("/auth/register", json=_foobar)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == VALID_USERNAME


def test_malformed_email(client):
    _foobar = foobar.copy()
    _foobar["email"] = "user@examplecom"
    response = client.post("/auth/register", json=_foobar)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_malformed_password(client):
    _foobar = foobar.copy()
    _foobar["password"] = "aaaAAA1a"
    response = client.post("/auth/register", json=_foobar)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert response.json()["detail"][0]["msg"] == VALID_PASSWORD


def test_non_existing_user_login(client):
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    assert response.status_code == InvalidCredentials.STATUS_CODE
    assert response.json()["detail"] == InvalidCredentials.DETAIL


def test_invalid_credentials(client):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token", data={"username": foobar["username"], "password": "aaaAAA1?"}
    )
    assert response.status_code == InvalidCredentials.STATUS_CODE
    assert response.json()["detail"] == InvalidCredentials.DETAIL


def test_invalid_token(client):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token", data={"username": foobar["username"], "password": "aaaAAA1!"}
    )
    token = response.json()["access_token"]
    response = client.get(
        "/auth/whoami", headers={"Authorization": f"Bearer {'.' + token[1:]}"}
    )
    assert response.status_code == InvalidToken.STATUS_CODE
    assert response.json()["detail"] == InvalidToken.DETAIL


def test_valid_credentials(client):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()


def test_unauthorized_whoami(client):
    response = client.get("/auth/whoami", headers={"Authorization": "Bearer "})
    assert response.status_code == LoginRequired.STATUS_CODE
    assert response.json()["detail"] == LoginRequired.DETAIL


def test_authorized_whoami(client):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    response = client.get("/auth/whoami", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"username": foobar["username"], "email": foobar["email"]}
