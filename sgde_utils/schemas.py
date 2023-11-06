import re
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, validator, root_validator


class SGDEBaseModel(BaseModel):
    """
    Base class for all models in the SGDE API. This class handles
    ORM mode and enum values.
    """

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


class UserBase(SGDEBaseModel):
    """
    Base class for the SGDE API users.
    """

    username: str = Field(min_length=4, max_length=32)
    email: EmailStr

    @validator("username")
    def valid_username(cls, username: str) -> str:
        if not re.match(USERNAME_PATTERN, username):
            raise ValueError(VALID_USERNAME)
        return username


class UserCreate(UserBase):
    """
    Class for creating a new user.
    """

    password: str = Field(min_length=8, max_length=32)

    @validator("password")
    def valid_password(cls, password: str) -> str:
        if not re.match(STRONG_PASSWORD_PATTERN, password):
            raise ValueError(VALID_PASSWORD)
        return password


class User(UserBase):
    """
    Class for the SGDE API users.
    """

    pass


class DataStructure(str, Enum):
    """
    Enum class for the data format handled by the SGDE models.
    """

    image = "image"


class Task(str, Enum):
    """
    Enum class for the task handled by the SGDE models.
    """

    classification = "classification"


class GeneratorBase(SGDEBaseModel):
    """
    Base class for the SGDE API generators.
    """

    name: str = Field(min_length=4, max_length=64)

    data_name: str = Field(default=None)
    data_description: str = Field(default=None)
    data_structure: DataStructure = Field(default=None)
    data_length: int = Field(default=None)

    task: Task = Field(default=None)

    metric: str = Field(default=None)
    best_score: str = Field(default=None)
    best_score_real: str = Field(default=None)

    @validator("name")
    def valid_generator_name(cls, name: str) -> str:
        if not re.match(GENERATOR_NAME_PATTERN, name):
            raise ValueError(VALID_GENERATOR_NAME)
        return name


class GeneratorExtended(GeneratorBase):
    """
    Class for creating a new generator.
    """

    class Config:
        extra = "allow"

    @root_validator(pre=True)
    def validate_extra_keys(cls, values):
        for key, value in values.items():
            if key not in cls.__fields__:
                if not isinstance(value, (str, int, float, list)):
                    raise ValueError(f"Value of {key} is not of allowed type.")
                if isinstance(value, list):
                    if not all(isinstance(item, (str, int, float)) for item in value):
                        raise ValueError(
                            f"Items in the list of {key} are not of allowed type."
                        )

        return values


class Generator(GeneratorBase):
    """
    Class for the SGDE API generators.
    """

    owner: str = Field()
    has_cls: bool = Field()
