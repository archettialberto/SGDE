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


def preprocess_metadata(metadata: dict) -> GeneratorCreate:
    return GeneratorCreate(
        name=metadata["name"],
        description=metadata["description"],
        dataset_name=metadata["dataset_name"],
        dataset_description=metadata["data_description"],
        format=metadata["data_format"],
        image_size=metadata["image_size"],
        conditioned=metadata["conditioned"],
        task=metadata["task"],
        num_classes=metadata["num_classes"],
        model_size=metadata["model_size"],
        generator_epochs=metadata["epochs"],
        generator_batch_size=metadata["batch_size"],
        classifier_epochs=metadata["classifier_epochs"],
        classifier_batch_size=metadata["batch_size"],
        discriminator_rounds=metadata["discriminator_rounds"],
        generator_input_shape=metadata["generator_input_shape"],
        classifier_gen_best_accuracy=metadata["classifier_gen_best_accuracy"],
        classifier_real_best_accuracy=metadata["classifier_real_best_accuracy"],
        ssim=metadata["SSIM"].numpy().astype(float).item(),
        avg_ssim=metadata["Averaged_SSIM"].numpy().astype(float).item(),
    )


def upload_generator(path: str, metadata: dict) -> Generator:
    parsed_metadata = preprocess_metadata(metadata)
    response = upload_generator_request(path=path, metadata=parsed_metadata)
    generator = Generator(**response.json())
    logger.info(f"Generator uploaded as {response.json()['name']}")
    return generator
