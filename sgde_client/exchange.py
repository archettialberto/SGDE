import pandas as pd

from sgde_client.utils import send_request


@send_request(method="GET", authenticate=True)
def get_tasks_request():
    return "exchange/tasks", {}


def get_tasks() -> pd.DataFrame:
    resp = get_tasks_request()
    df = pd.DataFrame(resp.json()["tasks"])
    return df


@send_request(method="POST", authenticate=True)
def post_task_request(task_data: dict):
    return "exchange/tasks", task_data


def post_task(task_name: str):
    post_task_request({"task_name": task_name})


@send_request(method="GET", authenticate=True)
def get_generators_request(task_name: str):
    return "exchange/generators", {"task_name": task_name}


def get_generators(task_name: str) -> pd.DataFrame:
    resp = get_generators_request(task_name)
    df = pd.DataFrame(resp.json()["generators"])
    return df


@send_request(method="POST", authenticate=True)
def post_generator_request(task_name: str, generator_data: dict):
    return "exchange/generators", {"task_name": task_name, **generator_data}


def upload_generator(task_name: str, generator_name: str, onnx_data: str):
    post_generator_request({"task_name": task_name, "generator_name": generator_name, "onnx": onnx_data})


@send_request(method="GET", authenticate=True)
def get_generator_request(task_name: str, generator_name: str):
    return "exchange/generators", {"task_name": task_name, "generator_name": generator_name}


def download_generator(task_name: str, generator_name: str) -> str:
    resp = get_generator_request(task_name, generator_name)
    return resp.json()["onnx"]
