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

    resp = query_api("auth/login",
                     data={"username": "babbala", "password": "aaaa8888AAAA#"},
                     get=False)
    print_resp(resp)
    token = resp["access_token"]

    resp = query_api("auth/whoami",
                     headers={"Authorization": f"Bearer {token}"},
                     get=True)
    print_resp(resp)

    resp = query_api("exchange/tasks",
                     headers={"Authorization": f"Bearer {token}"},
                     data={"task_name": "MNIST"},
                     get=False)
    print_resp(resp)

    resp = query_api("exchange/generators/upload",
                     headers={"Authorization": f"Bearer {token}"},
                     data={"task_name": "MNIST", "generator_name": "gen_CNN", "onnx": "onnx_content"},
                     get=False)
    print_resp(resp)

    resp = query_api("exchange/tasks",
                     headers={"Authorization": f"Bearer {token}"},
                     get=True)
    print_resp(resp)
    print(resp["tasks"])

    resp = query_api("exchange/generators",
                     headers={"Authorization": f"Bearer {token}"},
                     data={"task_name": "MNIST"},
                     get=True)
    print_resp(resp)
    print(resp["generators"])

    resp = query_api("exchange/generators/download",
                     headers={"Authorization": f"Bearer {token}"},
                     data={"task_name": "MNIST", "generator_name": "gen_CNN"},
                     get=True)
    print_resp(resp)
    print(resp["onnx"])
