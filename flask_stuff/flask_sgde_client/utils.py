import json
import logging
import os
from getpass import getpass

import requests

from flask_sgde_client.exceptions import ClientException, ResponseException


def ask_credentials():
    username = str(input("Insert username: "))
    password = str(getpass("Insert password: "))
    return username, password


def get_env_var(field: str, exists=True):
    if exists and field not in os.environ:
        raise ClientException(f"Field '{field}' must be set as environment variable")
    return os.environ[field]


def send_request(method: str, authenticate: bool = False):
    def decorator_fn(fn):
        def wrapper_fn(*args, **kwargs):
            if method not in ["GET", "POST"]:
                raise ClientException(f"Method must be either 'GET' or 'POST', not {method}")

            ip, port = get_env_var("SGDE_SERVER_IP"), get_env_var("SGDE_SERVER_PORT")

            uri, data = fn(*args, **kwargs)

            headers = {}

            if authenticate:
                if "SGDE_ACCESS_TOKEN" not in os.environ:
                    raise ClientException("You must login first")

                token = get_env_var("SGDE_ACCESS_TOKEN")
                headers["Authorization"] = f"Bearer {token}"

            request_fn = requests.get if method == "GET" else requests.post
            logging.info(f"[{method}] {ip}:{port}/{uri}")
            resp = request_fn(f"http://{ip}:{port}/{uri}", headers=headers, data=data)

            try:
                if resp.status_code not in [200, 201]:
                    raise ResponseException(resp.status_code, resp.json()["msg"])
                logging.info(f"[{resp.status_code}] {resp.json()['msg']}")
            except json.JSONDecodeError:
                logging.error(f"[{resp.status_code}] Response not in valid JSON format")

            return resp

        return wrapper_fn
    return decorator_fn


def safe_exception_raise_on_client(fn):
    def wrapper_fn(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ClientException as e:
            logging.error(e.message)

    wrapper_fn.__name__ = fn.__name__
    return wrapper_fn
