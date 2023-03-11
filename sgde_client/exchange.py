import os.path
import uuid

import pandas as pd

from utils import get_request, post_request


@get_request()
def get_generators_request(skip: int = 0, limit: int = 10):
    return f"generators?skip={skip}&limit={limit}", {}


def get_generators(skip: int = 0, limit: int = 10):
    response = get_generators_request(skip=skip, limit=limit)
    return pd.DataFrame(response.json())


@get_request()
def get_generator_request(generator_name: str):
    return f"generators/{generator_name}", {}


def get_generator(generator_name: str):
    response = get_generator_request(generator_name=generator_name)
    return pd.DataFrame([response.json()])


@get_request(authenticate=True)
def download_generator_request(generator_name: str):
    return f"generators/{generator_name}/download", {}


def download_generator(generator_name: str, path: str | None = None):
    response = download_generator_request(generator_name=generator_name)
    if path is None:
        path = os.path.join(os.getcwd(), f"{generator_name}_{uuid.uuid4()}.onnx")
    elif not path.endswith(".onnx"):
        path = os.path.join(path, f"{generator_name}_{uuid.uuid4()}.onnx")
    with open(path, "wb") as f:
        f.write(response)
    print(f"Generator downloaded at {path}")


@post_request(authenticate=True)
def upload_generator_request(path: str, metadata: dict):
    with open(path, "rb") as f:
        onnx = f.read()
    return f"exchange/upload", {"data": metadata, "files": {"onnx_file": onnx}}


def upload_generator():
    response = upload_generator_request()
    print(f"Generator uploaded as {response.json()['name']}")
