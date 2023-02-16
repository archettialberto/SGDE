import os
from getpass import getpass

from sgde_client.utils import send_request, ask_credentials, safe_exception_raise_on_client


@safe_exception_raise_on_client
@send_request(method="POST")
def register():
    username = str(input("Insert username: "))
    password = str(getpass("Insert password: "))
    rep_password = str(getpass("Confirm password: "))

    if password != rep_password:
        raise RuntimeError("Passwords must match")

    return "auth/register", {"data": {"username": username, "password": password}}


@send_request(method="POST")
def _send_login(usr, pwd):
    return "auth/login", {"data": {"username": usr, "password": pwd}}


@safe_exception_raise_on_client
def login():
    username, password = ask_credentials()
    resp = _send_login(username, password)
    os.environ["SGDE_ACCESS_TOKEN"] = str(resp.json()["access_token"])
