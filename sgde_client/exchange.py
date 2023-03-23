import os.path
from datetime import datetime

import pandas as pd

from schemas import Generator, GeneratorCreate
from sgde_client import logger
from sgde_client.utils import get_request, post_request


@get_request()
def get_generators_request(skip: int = 0, limit: int = 10):
    return f"generators/?skip={skip}&limit={limit}", {}


def get_generators(skip: int = 0, limit: int = 10) -> pd.DataFrame:
    response = get_generators_request(skip=skip, limit=limit)
    return pd.DataFrame(response.json())


@get_request()
def get_generator_request(generator_name: str):
    return f"generators/{generator_name}", {}


def get_generator(generator_name: str) -> Generator:
    response = get_generator_request(generator_name=generator_name)
    return Generator(**response.json())


@get_request(authenticate=True)
def download_generator_request(generator_name: str):
    return f"generators/{generator_name}/download", {}


def download_generator(generator_name: str, path: str = None) -> str:
    response = download_generator_request(generator_name=generator_name)
    filename = f"{generator_name}_{datetime.utcnow().strftime('%y%m%d%H%M%S')}.onnx"
    if path is None:
        path = os.path.join(os.getcwd(), filename)
    elif not path.endswith(".onnx"):
        path = os.path.join(path, filename)
    with open(path, "wb") as f:
        f.write(response.content)
    logger.info(f"Generator downloaded at {path}")
    return path


@post_request(authenticate=True)
def upload_generator_request(path: str, metadata: GeneratorCreate):
    with open(path, "rb") as f:
        onnx = f.read()
    return f"exchange/upload", {"data": metadata.dict(), "files": {"onnx_file": onnx}}


def upload_generator(path: str, metadata: GeneratorCreate) -> Generator:
    response = upload_generator_request(path=path, metadata=metadata)
    generator = Generator(**response.json())
    logger.info(f"Generator uploaded as {response.json()['name']}")
    return generator
