from datetime import timedelta, datetime

import bcrypt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import Field
from sqlalchemy.orm import Session

from sgde_api.auth.exceptions import (
    EmailTaken,
    UsernameTaken,
    UserNotFound,
    InvalidToken,
    LoginRequired,
    InvalidCredentials,
)
from sgde_utils.schemas import UserCreate, UserBase, SGDEBaseModel
from sgde_api.config import settings
from sgde_api.database import UserTable, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class UserDB(UserBase):
    """
    User class in the database.
    """

    hashed_password: bytes


def get_user_by_username(db: Session, username: str) -> UserDB | None:
    """
    Get a user by username. Returns None if not found.
    :param db: database session
    :param username: username to search
    :return: UserDB object or None
    """
    return db.query(UserTable).filter_by(username=username).first()


def get_user_by_username_required(db: Session, username: str) -> UserDB:
    """
    Get a user by username. Raises UserNotFound if not found.
    :param db: database session
    :param username: username to search
    :return: UserDB object
    """
    user = get_user_by_username(db, username)
    if not user:
        raise UserNotFound()
    return user


def get_user_by_email(db: Session, email: str) -> UserDB | None:
    """
    Get a user by email. Returns None if not found.
    :param db: database session
    :param email: email to search
    :return: UserDB object or None
    """
    return db.query(UserTable).filter_by(email=email).first()


def get_users(db: Session) -> list[UserDB]:
    """
    Get all users.
    :param db: database session
    :return: list of UserDB objects
    """
    return db.query(UserTable).offset(0).all()


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    b_plain_password = plain_password.encode()
    return bcrypt.checkpw(b_plain_password, hashed_password)


def get_password_hash(password: str) -> bytes:
    b_password = password.encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(b_password, salt)
    return hashed


def create_user(db: Session, user: UserCreate) -> UserDB:
    """
    Insert a user in the database.
    :param db: database session
    :param user: user to insert
    :return: UserDB object
    """
    if get_user_by_username(db, user.username):
        raise UsernameTaken()
    if get_user_by_email(db, user.email):
        raise EmailTaken()
    hashed_password = get_password_hash(user.password)
    db_user = UserTable(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_access_token(
    user: UserDB, expires_delta: timedelta = timedelta(minutes=settings.JWT_EXP)
):
    """
    Create a JWT token for a user session.
    :param user: UserDB object
    :param expires_delta: expiration time
    :return: JWT token
    """
    jwt_data = {"sub": user.username, "exp": datetime.utcnow() + expires_delta}
    return jwt.encode(jwt_data, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


class JWTData(SGDEBaseModel):
    """
    Class for the content of a JWT token.
    """

    username: str = Field(alias="sub")


def parse_jwt_user_data(token: str = Depends(oauth2_scheme)) -> JWTData | None:
    """
    Parse a JWT token and return the user data. Returns None if token is None.
    :param token: JWT token
    :return: JWTData object or None
    """
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError as exc:
        raise InvalidToken() from exc
    return JWTData(**payload)


def parse_jwt_user_data_required(
    token: JWTData | None = Depends(parse_jwt_user_data),
) -> JWTData:
    """
    Parse a JWT token and return the user data. Raises LoginRequired if token is None.
    :param token: JWT token
    :return: JWTData object
    """
    if not token:
        raise LoginRequired()
    return token


def authenticate_user(db: Session, username: str, password: str) -> UserDB:
    """
    Authenticate a user given a username and password.
    :param db: database session
    :param username: username to search
    :param password: password to verify
    :return: UserDB object
    """
    user = get_user_by_username(db, username)
    if not user:
        raise InvalidCredentials()
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentials()
    return user


class Token(SGDEBaseModel):
    """
    Class for the user's access token.
    """

    access_token: str
    token_type: str = "bearer"


def create_access_token_for_auth_user(
    db: Session, username: str, password: str
) -> Token:
    """
    Create a JWT token for a user session.
    :param db: database session
    :param username: username of the logged user
    :param password: password of the logged user
    :return: JWT token
    """
    user = authenticate_user(db, username, password)
    access_token = create_access_token(user)
    return Token(access_token=access_token)


def get_current_user(
    db: Session = Depends(get_db),
    token: JWTData = Depends(parse_jwt_user_data_required),
) -> UserDB:
    """
    Get the current user given a JWT token.
    :param db: database session
    :param token: JWT token
    :return: UserDB object
    """
    return get_user_by_username_required(db=db, username=token.username)
