import re

from pydantic import EmailStr, Field, validator

from src.schemas import SGDEBaseModel

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


class UserDB(UserBase):
    hashed_password: bytes


class User(UserBase):
    pass


class JWTData(SGDEBaseModel):
    username: str = Field(alias="sub")


class Token(SGDEBaseModel):
    access_token: str
    token_type: str = "bearer"
