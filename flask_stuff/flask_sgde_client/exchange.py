import pandas as pd

from flask_sgde_client.utils import send_request, safe_exception_raise_on_client


@send_request(method="GET", authenticate=True)
def get_tasks_request():
    return "exchange/tasks", {}


@safe_exception_raise_on_client
def get_tasks() -> pd.DataFrame:
    resp = get_tasks_request()
    df = pd.DataFrame(resp.json()["tasks"])
    return df


@send_request(method="POST", authenticate=True)
def post_task_request(task_data: dict):
    return "exchange/tasks", task_data


@safe_exception_raise_on_client
def post_task(task_name: str):
    post_task_request({"task_name": task_name})


@send_request(method="GET", authenticate=True)
def get_generators_request(task_name: str):
    return "exchange/generators", {"task_name": task_name}


@safe_exception_raise_on_client
def get_generators(task_name: str) -> pd.DataFrame:
    resp = get_generators_request(task_name)
    df = pd.DataFrame(resp.json()["generators"])
    return df


@send_request(method="POST", authenticate=True)
def post_generator_request(task_name: str, generator_data: dict):
    return "exchange/generators/upload", {"task_name": task_name, **generator_data}


@safe_exception_raise_on_client
def upload_generator(task_name: str, generator_name: str, onnx_data: str):
    post_generator_request(task_name, {"generator_name": generator_name, "onnx": onnx_data})


@send_request(method="GET", authenticate=True)
def get_generator_request(task_name: str, generator_name: str):
    return "exchange/generators/download", {"task_name": task_name, "generator_name": generator_name}


@safe_exception_raise_on_client
def download_generator(task_name: str, generator_name: str) -> str:
    resp = get_generator_request(task_name, generator_name)
    return resp.json()["onnx"]
