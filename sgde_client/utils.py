import functools
import os
from json import JSONDecodeError

import requests

from sgde_client.exceptions import (
    ResponseException,
    MissingAuthorization,
    ServerUnreachable,
)
from sgde_client.config import settings, logger


def send_request(method: str, authenticate: bool = False):
    """
    Decorator for sending requests to the API.
    :param method: GET or POST
    :param authenticate: Whether to authenticate the request
    """

    def decorator_fn(fn):
        @functools.wraps(fn)
        def wrapped_fn(*args, **kwargs):
            if method == "GET":
                request_fn = requests.get
            elif method == "POST":
                request_fn = requests.post
            else:
                raise ValueError(f"Method must be either 'GET' or 'POST', not {method}")

            uri, payload = fn(*args, **kwargs)

            if authenticate:
                if "ACCESS_TOKEN" not in os.environ:
                    raise MissingAuthorization()
                token = os.getenv("ACCESS_TOKEN")
                if "headers" not in payload:
                    payload["headers"] = {}
                payload["headers"]["Authorization"] = f"Bearer {token}"

            url = f"http://{settings.API_IP}:{settings.API_PORT}/{uri}"
            if settings.DEBUG_MODE:
                logger.info(f"Sending {method} request to {url}")
            try:
                resp = request_fn(url, **payload)
            except requests.ConnectionError:
                raise ServerUnreachable()

            if resp.status_code not in [200, 201]:
                try:
                    raise ResponseException(resp.status_code, str(resp.json()))
                except JSONDecodeError:
                    raise ResponseException(
                        resp.status_code, "Cannot decode JSON response"
                    )

            if settings.DEBUG_MODE:
                try:
                    logger.info(f"Received {resp.status_code}, {resp.json()}")
                except JSONDecodeError:
                    logger.warning(
                        f"Received {resp.status_code}, but cannot decode JSON response"
                    )
            return resp

        return wrapped_fn

    return decorator_fn


def get_request(authenticate: bool = False):
    """
    Decorator for sending GET requests to the API.
    :param authenticate: Whether to authenticate the request
    """
    return send_request(method="GET", authenticate=authenticate)


def post_request(authenticate: bool = False):
    """
    Decorator for sending POST requests to the API.
    :param authenticate: Whether to authenticate the request
    """
    return send_request(method="POST", authenticate=authenticate)
