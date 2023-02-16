import os
import shutil
from pathlib import Path

import pytest

from sgde_server.exceptions import MissingFieldException, InvalidFormatException, AlreadyExistsException, \
    DoesNotExistException, APIException
from sgde_server import create_app


@pytest.fixture()
def app():
    app = create_app(instance_path=Path(os.getcwd(), "test_instance"))
    app.config.update({"TESTING": True})
    yield app
    shutil.rmtree(app.instance_path)


@pytest.fixture()
def client(app):
    return app.test_client()


def check_exception(resp, exception: APIException):
    assert resp.status_code == exception.status_code and resp.json["msg"] == exception.msg


def test_register_request(app, client):
    resp = client.post("/auth/register")
    check_exception(resp, MissingFieldException("username"))

    resp = client.post("/auth/register", data={"username": "foo_bar"})
    check_exception(resp, MissingFieldException("password"))

    resp = client.post("/auth/register", data={"username": "foo", "password": "aaaaAAAA1111!"})
    check_exception(resp, InvalidFormatException("username", InvalidFormatException.TOO_SHORT))

    long_username = 'foo' * app.config['MAX_USERNAME_LENGTH']
    resp = client.post("/auth/register", data={"username": f"{long_username}", "password": "aaaaAAAA1111!"})
    check_exception(resp, InvalidFormatException("username", InvalidFormatException.TOO_LONG))

    long_password = 'aaaaAAAA1111!' * app.config['MAX_PASSWORD_LENGTH']
    resp = client.post("/auth/register", data={"username": f"foo_bar", "password": f"{long_password}"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.TOO_LONG))

    resp = client.post("/auth/register", data={"username": "1foo_bar", "password": "aaaaAAAA1111!"})
    check_exception(resp, InvalidFormatException("username", InvalidFormatException.MUST_START_WITH_CHAR))

    resp = client.post("/auth/register", data={"username": "foo bar", "password": "aaaaAAAA1111!"})
    check_exception(resp, InvalidFormatException("username", InvalidFormatException.USR_CHARS))

    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaAAAAaaaa!"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_NUMBER))

    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaAAAA1111"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_SYMBOL))

    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "AAAAAAAA1111!"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_L_CHAR))

    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaaaaa1111!"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_U_CHAR))

    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201

    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    check_exception(resp, AlreadyExistsException("username"))


def test_login_request(app, client):
    resp = client.post("/auth/login")
    check_exception(resp, MissingFieldException("username"))

    resp = client.post("/auth/login", data={"username": "foo_bar"})
    check_exception(resp, MissingFieldException("password"))

    resp = client.post("/auth/login", data={"username": "foo", "password": "aaaaAAAA1111!"})
    check_exception(resp, InvalidFormatException("username", InvalidFormatException.TOO_SHORT))

    long_username = 'foo' * app.config['MAX_USERNAME_LENGTH']
    resp = client.post("/auth/login", data={"username": f"{long_username}", "password": "aaaaAAAA1111!"})
    check_exception(resp, InvalidFormatException("username", InvalidFormatException.TOO_LONG))

    long_password = 'aaaaAAAA1111!' * app.config['MAX_PASSWORD_LENGTH']
    resp = client.post("/auth/login", data={"username": f"foo_bar", "password": f"{long_password}"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.TOO_LONG))

    resp = client.post("/auth/login", data={"username": "1foo_bar", "password": "aaaaAAAA1111!"})
    check_exception(resp, InvalidFormatException("username", InvalidFormatException.MUST_START_WITH_CHAR))

    resp = client.post("/auth/login", data={"username": "foo bar", "password": "aaaaAAAA1111!"})
    check_exception(resp, InvalidFormatException("username", InvalidFormatException.USR_CHARS))

    resp = client.post("/auth/login", data={"username": "foo_bar", "password": "aaaaAAAAaaaa!"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_NUMBER))

    resp = client.post("/auth/login", data={"username": "foo_bar", "password": "aaaaAAAA1111"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_SYMBOL))

    resp = client.post("/auth/login", data={"username": "foo_bar", "password": "AAAAAAAA1111!"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_L_CHAR))

    resp = client.post("/auth/login", data={"username": "foo_bar", "password": "aaaaaaaa1111!"})
    check_exception(resp, InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_U_CHAR))

    _ = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})

    resp = client.post("/auth/login", data={"username": "foo_bar_baz", "password": "aaaaAAAA1111!"})
    check_exception(resp, DoesNotExistException("username"))

    example_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY3NjQ3MjkyNCwianRpIjoiNGE5ZGFjZDctNGQyOS00YWQyLTgwMWQtODBjMDEyZWY5NWUxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImZvb19iYXIiLCJuYmYiOjE2NzY0NzI5MjQsImV4cCI6MTY3NjU1OTMyNH0.NqXv-MFtH7VMDp3VNg6pX0Mm2YvwJXptfY39VoTSAOa'
    resp = client.get("/auth/whoami", headers={"Authorization": f"Bearer {example_token}"})
    assert resp.status_code == 422
    assert resp.json["msg"] == "Signature verification failed"

    resp = client.post("/auth/login", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201
    assert "access_token" in resp.json

    token = resp.json["access_token"]
    resp = client.get("/auth/whoami", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "foo_bar" in resp.json["msg"]
