from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, EmailStr

from sgde_api_legacy.settings import get_settings

settings = get_settings()


class UserBase(BaseModel):
    username: str = Field(**get_settings().sgde_username_params)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(**get_settings().sgde_password_params)


class User(UserBase):
    created: datetime

    class Config:
        orm_mode = True


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


class GeneratorBase(BaseModel):
    name: str = Field(**get_settings().sgde_generator_name_params)
    conditioned: bool
    data_format: DataFormat
    task: Task | None
    num_classes: int | None = Field(ge=2)
    model_size: ModelSize
    epochs: int = Field(ge=1)
    batch_size: int = Field(ge=1)
    description: str = Field(**get_settings().sgde_generator_description_params)


class GeneratorCreate(GeneratorBase):
    pass


class Generator(GeneratorBase):
    owner: str = Field(**get_settings().sgde_username_params)
    created: datetime

    class Config:
        orm_mode = True
