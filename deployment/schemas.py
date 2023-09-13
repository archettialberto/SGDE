import inspect
import re
from enum import Enum
from typing import Type

from fastapi import Form
from pydantic import BaseModel, Field, EmailStr, validator


class SGDEBaseModel(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True


GENERATOR_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
VALID_GENERATOR_NAME = (
    "Generator name must contain characters, digits, and dashes;"
    "generator name must start with a character"
)
USERNAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")
VALID_USERNAME = (
    "Username must contain characters, digits, and dashes;"
    "username must start with a character"
)
STRONG_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z\d\W]+$"
)
VALID_PASSWORD = (
    "Password must contain at least one lower character, "
    "one upper character, "
    "one digit, "
    "and one special symbol"
)


def as_form(cls: Type[BaseModel]):
    new_parameters = []

    for field_name, model_field in cls.__fields__.items():
        model_field: ModelField  # type: ignore

        new_parameters.append(
            inspect.Parameter(
                model_field.alias,
                inspect.Parameter.POSITIONAL_ONLY,
                default=Form(...)
                if model_field.required
                else Form(model_field.default),
                annotation=model_field.outer_type_,
            )
        )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig  # type: ignore
    setattr(cls, "as_form", as_form_func)
    return cls


class UserBase(SGDEBaseModel):
    username: str = Field(min_length=4, max_length=32)
    email: EmailStr

    @validator("username")
    def valid_username(cls, username: str) -> str:
        if not re.match(USERNAME_PATTERN, username):
            raise ValueError(VALID_USERNAME)
        return username


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=32)

    @validator("password")
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(VALID_PASSWORD)
        return password


class User(UserBase):
    pass


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
    name: str = Field(min_length=4, max_length=64)
    description: str
    dataset_name: str = Field(default=None)
    dataset_description: str = Field(default=None)
    format: DataFormat
    image_size: int = Field(default=None)
    conditioned: bool = Field(default=False)
    task: Task
    num_classes: int = Field(default=None, ge=2)
    model_size: ModelSize
    generator_epochs: int = Field(ge=1)
    generator_batch_size: int = Field(ge=1)
    classifier_epochs: int = Field(ge=0)
    classifier_batch_size: int = Field(ge=1)
    discriminator_rounds: int = Field(default=3, ge=0)
    generator_input_shape: int = Field(ge=1)
    classifier_gen_best_accuracy: float = Field(ge=0.0)
    classifier_real_best_accuracy: float = Field(ge=0.0)
    ssim: float
    avg_ssim: float

    @validator("name")
    def valid_generator_name(cls, name: str) -> str:
        if not re.match(GENERATOR_NAME_PATTERN, name):
            raise ValueError(VALID_GENERATOR_NAME)
        return name


@as_form
class GeneratorCreate(GeneratorBase):
    pass


class Generator(GeneratorBase):
    owner: str = Field()
