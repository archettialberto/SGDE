import re
from enum import Enum

from pydantic import Field, validator

from sgde_api.schemas import SGDEBaseModel

GENERATOR_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{3,15}$")
VALID_GENERATOR_NAME = "Generator name must contain characters, digits, and dashes;" \
                       "generator name must start with a character"


class DataFormat(str, Enum):
    image = "image"
    tabular = "tabular"


class Task(str, Enum):
    classification = "classification"
    regression = "regression"


class ModelSize(str, Enum):
    small = "small"
    medium = "medium"
    large = "large"


class GeneratorBase(SGDEBaseModel):
    name: str = Field(min_length=4, max_length=16)
    conditioned: bool
    data_format: DataFormat
    task: Task | None
    num_classes: int | None = Field(ge=2)
    model_size: ModelSize
    epochs: int = Field(ge=1)
    batch_size: int = Field(ge=1)
    description: str

    @validator("name")
    def valid_username(cls, username: str) -> str:
        if not re.match(GENERATOR_NAME_PATTERN, username):
            raise ValueError(VALID_GENERATOR_NAME)
        return username


class GeneratorCreate(GeneratorBase):
    pass


class GeneratorDB(GeneratorBase):
    owner: str
    filename: str


class Generator(GeneratorBase):
    owner: str
