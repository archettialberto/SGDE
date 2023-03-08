import numpy as np
import re
from pydantic import Field, validator, BaseModel

from sgde_server.exchange.schemas import DataFormat, Task, ModelSize


class MetadataBase(BaseModel):
    data_shape: tuple[int] | tuple[int, int] | tuple[int, int, int]
    data_format: DataFormat

    task: Task | None

    conditioned: bool = True
    num_classes: int | None = Field(ge=2)

    model_size: ModelSize
    padding: bool = False

    epochs: int = Field(ge=1)
    batch_size: int = Field(ge=1)

    class Config:
        orm_mode = True


class Metadata(MetadataBase):
    name: str = Field(min_length=4, max_length=16)
    description: str = Field(min_length=4, max_length=1000)

    @validator("name")
    def valid_username(cls, username: str) -> str:
        if not re.match(re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{3,15}$"), username):
            raise ValueError("Generator name must contain characters, digits, and dashes;"
                             "generator name must start with a character")
        return username


def metadata_extraction(
        *,
        X: np.array,
        y: np.array = None,
        epochs: int,
        batch_size: int,
        conditioned: bool = True,
        data_format: str = 'image',
        model_size: str = 'medium',
        task: str = 'classification',
        padding: bool = False
):
    """
    -1: error
    """
    metadata = {}
    metadata['shape'] = data.shape

    if data_format == 'image':
        metadata['data_format'] = 'image'
        if len(data.shape) > 4 or len(data.shape) < 3:
            print(f'ABORT: {data.shape} is not a proper shape for an image dataset')
            return -1
        elif len(data.shape) == 3:
            metadata['shape'] = data.shape + (1,)
            metadata['expand_shape'] = True
        else:
            metadata['expand_shape'] = False
    else:
        return -1

    if conditioned:
        assert len(data) == len(labels)
        assert len(labels.shape) == 1 or (len(labels.shape) == 2 and labels.shape[1] == 1)
        metadata['conditioned'] = True
        metadata['labels_shape'] = labels.shape
        if task == 'classification':
            metadata['task'] = 'classification'
            metadata['classes'] = np.unique(labels)
            metadata['num_classes'] = len(np.unique(labels))
        else:
            metadata['task'] = None

    else:
        metadata['conditioned'] = False
        metadata['task'] = None

    # Model section
    metadata['model_size'] = model_size
    metadata['epochs'] = epochs
    metadata['batch_size'] = batch_size
    metadata['padding'] = padding  # Implementare logica di padding rispetto alla profondità massima
    metadata['max_blocks'] = 2  # Implementare logica per il calcolo della dimensione massima

    metadata['leraning_rate'] = 1e-4
    metadata['discriminator_rounds'] = 3

    if model_size == 'medium':
        metadata['blocks'] = min(2, metadata['max_blocks'])
        metadata['filters'] = 64
        metadata['embedding_dim'] = 64
        metadata['latent_dim'] = 128

    return metadata
