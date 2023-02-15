import json
import logging
import os
from getpass import getpass

import requests


class ClientError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ResponseError(ClientError):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"[Status {status_code}] {message}")


def ask_credentials():
    username = str(input("Insert username: "))
    password = str(getpass("Insert password: "))
    return username, password


def get_env_var(field: str, exists=True):
    if exists and field not in os.environ:
        raise ClientError(f"Field '{field}' must be set as environment variable")
    return os.environ[field]


def handle_error_status(resp):
    if resp.status_code not in [200, 201]:
        raise ResponseError(resp.status_code, json.loads(resp.text).get("msg"))


def send_request(method: str, authenticate: bool = False):
    def decorator_fn(fn):
        def wrapped_fn(*args, **kwargs):
            if method not in ["GET", "POST"]:
                raise ClientError(f"Method must be either 'GET' or 'POST', not {method}")

            ip, port = get_env_var("SGDE_SERVER_IP"), get_env_var("SGDE_SERVER_PORT")

            uri, kwargs = fn(*args, **kwargs)

            if authenticate:
                if "SGDE_ACCESS_TOKEN" not in os.environ:
                    raise ClientError("You must login first")

                token = get_env_var("SGDE_ACCESS_TOKEN")
                kwargs["headers"]["Authorization"] = f"Bearer {token}"

            request_fn = requests.get if method == "GET" else requests.post
            resp = request_fn(f"http://{ip}:{port}/{uri}", **kwargs)

            handle_error_status(resp)

            return resp

        return wrapped_fn
    return decorator_fn


def safe_exception_raise_on_client(fn):
    def wrapper_fn(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ClientError as e:
            logging.error(e.message)
            exit(1)

    wrapper_fn.__name__ = fn.__name__
    return wrapper_fn
