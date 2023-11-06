import json
import os.path
import zipfile
from datetime import datetime
from typing import Optional

import pandas as pd

from sgde_client.config import logger
from sgde_utils.schemas import Generator, GeneratorExtended
from sgde_client.utils import get_request, post_request


@get_request()
def get_generators_request():
    """Get all generators HTTP request"""
    return f"generators", {}


def get_generators() -> pd.DataFrame:
    """Get all generators"""
    response = get_generators_request()
    return pd.DataFrame(response.json())


@get_request()
def get_generator_request(generator_name: str):
    """Get a single generator metadata HTTP request"""
    return f"generators/{generator_name}", {}


def get_generator_metadata(generator_name: str) -> Generator:
    """Get a single generator metadata"""
    response = get_generator_request(generator_name=generator_name)
    return Generator(**response.json())


@get_request(authenticate=True)
def download_generator_request(generator_name: str):
    """Download a single generator HTTP request"""
    return f"generators/{generator_name}/download", {}


def download_generator(generator_name: str) -> dict:
    """Download a single generator (both ONNX and JSON files with metadata)"""
    response = download_generator_request(generator_name=generator_name)
    t = datetime.utcnow().strftime("%y%m%d%H%M%S")
    zip_filename = f"{generator_name}_{t}.zip"
    zip_path = os.path.join(os.getcwd(), zip_filename)
    with open(zip_path, "wb") as f:
        f.write(response.content)
    logger.info(f"Generator downloaded at {zip_path}")
    gen_onnx_filename = f"{generator_name}_gen_{t}.onnx"
    cls_onnx_filename = f"{generator_name}_cls_{t}.onnx"
    json_filename = f"{generator_name}_{t}.json"
    gen_onnx_path = os.path.join(os.getcwd(), gen_onnx_filename)
    cls_onnx_path = os.path.join(os.getcwd(), cls_onnx_filename)
    json_path = os.path.join(os.getcwd(), json_filename)
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(os.getcwd())
        for filename in zip_ref.namelist():
            if filename.endswith(".json"):
                os.rename(os.path.join(os.getcwd(), filename), json_path)
            elif filename.endswith("_gen.onnx"):
                os.rename(os.path.join(os.getcwd(), filename), gen_onnx_path)
            elif filename.endswith("_cls.onnx"):
                os.rename(os.path.join(os.getcwd(), filename), cls_onnx_path)
    with open(json_path, "r") as f:
        metadata = json.load(f)
    os.remove(zip_path)
    os.remove(json_path)
    metadata["generator_path"] = gen_onnx_path
    if os.path.exists(cls_onnx_path):
        metadata["real_predictor_path"] = cls_onnx_path
    return metadata


@post_request(authenticate=True)
def upload_generator_request(metadata: dict, gen_path: str, cls_path: str):
    """Upload a generator HTTP request"""
    if os.path.isdir(gen_path):
        gen_path = os.path.join(gen_path, "model.onnx")
    with open(gen_path, "rb") as f:
        gen_onnx_file = f.read()
    if cls_path:
        if os.path.isdir(cls_path):
            cls_path = os.path.join(cls_path, "model.onnx")
        with open(cls_path, "rb") as f:
            cls_onnx_file = f.read()
    parsed_metadata = GeneratorExtended(**metadata)
    return f"exchange/upload", {
        "files": {
            "gen_onnx_file": gen_onnx_file,
            "cls_onnx_file": cls_onnx_file if cls_path else None,
            "json_file": parsed_metadata.json()
        }
    }


def upload_generator(metadata: dict) -> Generator:
    """Upload a generator"""
    gen_path = metadata["generator_path"]
    cls_path = metadata["real_predictor_path"] if "real_predictor_path" in metadata else None
    response = upload_generator_request(metadata=metadata, gen_path=gen_path, cls_path=cls_path)
    generator = Generator(**response.json())
    logger.info(f"Generator uploaded as {response.json()['name']}")
    return generator
