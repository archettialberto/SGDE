import os

from flask_sgde_client.utils import send_request, ask_credentials, safe_exception_raise_on_client


@send_request(method="POST")
def register_request(username: str, password: str):
    return "auth/register", {"username": username, "password": password}


@safe_exception_raise_on_client
def register(username: str = None, password: str = None):
    if username is None and password is None:
        username, password = ask_credentials()
    register_request(username, password)


@send_request(method="POST")
def login_request(username: str, password: str):
    return "auth/login", {"username": username, "password": password}


@safe_exception_raise_on_client
def login(username: str = None, password: str = None) -> str:
    if username is None and password is None:
        username, password = ask_credentials()
    resp = login_request(username, password)
    token = str(resp.json()["access_token"])
    os.environ["SGDE_ACCESS_TOKEN"] = token
    return token
