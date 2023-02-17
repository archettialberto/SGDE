import logging
import os

from sgde_client.utils import send_request, ask_credentials, safe_exception_raise_on_client


@safe_exception_raise_on_client
@send_request(method="POST")
def register_request():
    username, password = ask_credentials()
    return "auth/register", {"username": username, "password": password}


def register():
    register_request()


@safe_exception_raise_on_client
@send_request(method="POST")
def login_request():
    username, password = ask_credentials()
    return "auth/login", {"username": username, "password": password}


def login() -> str:
    resp = login_request()
    logging.info(resp.json["msg"])
    os.environ["SGDE_ACCESS_TOKEN"] = str(resp.json()["access_token"])
    return str(resp.json["access_token"])
