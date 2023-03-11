import re
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, validator


class SGDEBaseModel(BaseModel):
    class Config:
        orm_mode = True
        use_enum_values = True


GENERATOR_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{3,15}$")
VALID_GENERATOR_NAME = "Generator name must contain characters, digits, and dashes;" \
                       "generator name must start with a character"
USERNAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{3,15}$")
VALID_USERNAME = "Username must contain characters, digits, and dashes;" \
                 "username must start with a character"
STRONG_PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z\d\W]+$")
VALID_PASSWORD = "Password must contain at least one lower character, " \
                 "one upper character, " \
                 "one digit, " \
                 "and one special symbol"


class UserBase(SGDEBaseModel):
    username: str = Field(min_length=4, max_length=16)
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


class Generator(GeneratorBase):
    owner: str
