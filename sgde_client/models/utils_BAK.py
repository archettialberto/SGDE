from typing import Tuple

import numpy as np

import tensorflow.keras as tfk
import tensorflow.keras.layers as tfkl
from pydantic import Field, validator, root_validator

from sgde_client import logger
from schemas import SGDEBaseModel, DataFormat, Task, ModelSize


def scheduler(epoch, lr):
    if epoch == 60:
        return lr * 0.01
    if epoch == 80:
        return lr * 0.01
    else:
        return lr


class MetadataImageBase(SGDEBaseModel):
    data_name: str = Field(default=None)
    data_description: str = Field(default=None)
    X: np.array
    y: np.array
    image_size: int
    X_shape: Tuple[int]
    y_shape: Tuple[int] = Field(default=None)
    conditioned: bool = Field(default=False)
    data_format: DataFormat = DataFormat.image.value
    task: Task
    num_classes: int = Field(default=None, ge=2)
    model_size: ModelSize
    generator_epochs: int = Field(ge=1)
    generator_batch_size: int = Field(ge=1)
    classifier_epochs: int = Field(ge=0)
    classifier_batch_size: int = Field(ge=1)
    discriminator_rounds: int = Field(default=3, ge=0)
    blocks: int = Field(default=None, ge=0)
    filters: int = Field(default=None, ge=0)
    latent_dim: int = Field(default=None, ge=0)

    @validator("X_shape")
    def valid_X_shape(cls, X_shape, values):
        if not 3 <= len(X_shape) <= 4:
            raise ValueError(f"{X_shape} is not a valid shape for an image dataset")
        image_size = values.get("image_size")
        return [
            X_shape[0],
            image_size,
            image_size,
            X_shape[-1] if len(X_shape) == 4 else 1,
        ]

    @validator("y_shape")
    def valid_y_shape(cls, y_shape, values):
        if y_shape is not None:
            X_shape = values.get("X_shape")
            if X_shape[0] != y_shape[0]:
                raise ValueError(
                    f"Found a different number of samples and labels ({X_shape[0]}, {y_shape[0]})"
                )
        if len(y_shape) != 1 or (len(y_shape) == 2 and y_shape[1] != 1):
            raise ValueError(f"{y_shape} is not a valid label shape")
        return y_shape

    @root_validator
    def valid_blocks(cls, values):
        model_size = values.get("model_size")
        if model_size == ModelSize.small:
            values["blocks"] = 2
        elif model_size == ModelSize.medium:
            values["blocks"] = 3
        else:
            values["blocks"] = 4
        return values

    @root_validator
    def valid_filters(cls, values):
        model_size = values.get("model_size")
        if model_size == ModelSize.small:
            values["filters"] = 32
        elif model_size == ModelSize.medium:
            values["filters"] = 32
        else:
            values["filters"] = 64
        return values

    @root_validator
    def valid_latent_dim(cls, values):
        model_size = values.get("model_size")
        if model_size == ModelSize.small:
            values["latent_dim"] = 64
        elif model_size == ModelSize.medium:
            values["latent_dim"] = 128
        else:
            values["latent_dim"] = 128
        return values

    @root_validator
    def valid_num_classes(cls, values):
        task = values.get("task")
        conditioned = values.get("conditioned")
        y = values.get("y")
        if task == Task.classification and conditioned:
            if len(y.shape) == 1:
                values["num_classes"] = 2
            else:
                values["num_classes"] = len(np.unique(y))
        return values


class MetadataImagePreprocess(MetadataImageBase):
    X_max: float
    X_min: float
    generator_input_shape: Tuple[int] = Field(default=None)
    generator_output_shape: Tuple[int] = Field(default=None)
    discriminator_input_shape: Tuple[int] = Field(default=None)
    discriminator_output_shape: Tuple[int] = Field(default=None)


def extract_image_metadata(
    X: np.array,
    y: np.array = None,
    task: str = "classification",
    image_size: int = 32,
    model_size: str = "small",
    generator_epochs: int = 500,
    generator_batch_size: int = 128,
    classifier_epochs: int = 100,
    classifier_batch_size: int = 128,
) -> MetadataImageBase:
    return MetadataImageBase(
        X=X,
        y=y,
        X_shape=X.shape,
        y_shape=None if y is None else y.shape,
        task=task,
        conditioned=False if y is None else True,
        image_size=image_size,
        model_size=model_size,
        generator_epochs=generator_epochs,
        generator_batch_size=generator_batch_size,
        classifier_epochs=classifier_epochs,
        classifier_batch_size=classifier_batch_size,
    )


def preprocess_image_data(
    metadata: MetadataImageBase,
    verbose: bool = True,
) -> MetadataImagePreprocess:
    # Make the image dataset with 4 dimensions
    X = metadata.X
    if len(X.shape) == 3:
        X = np.expand_dims(metadata.X, axis=-1)

    # Make the image dataset squared
    if verbose:
        logger.info("Reshaping dataset...")
    dim = min(X.shape[1:-1])
    X = X[
        :,
        (X.shape[1] - dim) // 2 : (X.shape[1] + dim) // 2,
        (X.shape[2] - dim) // 2 : (X.shape[2] + dim) // 2,
        :,
    ]

    # Resize the image dataset
    if verbose:
        logger.info("Resizing dataset...")
    resize = tfkl.Resizing(metadata.image_size, metadata.image_size)
    X = resize(X).numpy()

    # Save data minimum and maximum
    X_min = X.min()
    X_max = X.max()

    # Normalize in range [-1,1]
    if verbose:
        logger.info("Normalizing data...")
    X = ((X - X_min) / (X_max - X_min) * 2 - 1).astype(np.float32)

    y = metadata.y
    if metadata.conditioned:
        y = tfk.utils.to_categorical(y)
        conditioned_args = {
            "generator_input_shape": metadata.latent_dim + metadata.num_classes,
            "generator_output_shape": metadata.X_shape,
            "discriminator_input_shape": metadata.X_shape,
            "discriminator_output_shape": (1,),
        }
        conditioned_args["discriminator_input_shape"][-1] += metadata.num_classes
    else:
        conditioned_args = {}

    base_metadata = metadata.dict()
    base_metadata["X"] = X
    base_metadata["y"] = y
    return MetadataImagePreprocess(
        **base_metadata,
        X_max=X_max,
        X_min=X_min,
        **conditioned_args,
    )
