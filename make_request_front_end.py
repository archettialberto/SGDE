import os

import requests


def print_resp(resp):
    print(f"Message: '{resp['msg']}'. Keys: {list(resp.keys())}.\n")


def query_api(query: str, headers: dict = None, data: dict = None, get: bool = True) -> dict:
    fn = requests.get if get else requests.post
    print(f"Running request '{query}' with {'GET' if get else 'POST'} method.")
    resp = fn(f"http://127.0.0.1:5000/{query}", headers=headers, data=data)
    return dict(resp.json())


if __name__ == "__main__":
    resp = query_api("auth/register",
                     data={"username": "babbala", "password": "aaaa8888AAAA#"},
                     get=False)
    print_resp(resp)

    os.environ["SGDE_SERVER_IP"] = "127.0.0.1"
    os.environ["SGDE_SERVER_PORT"] = "5000"

    from sgde_client import register, login

    # register()
    login()
