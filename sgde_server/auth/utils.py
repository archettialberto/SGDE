from datetime import timedelta, datetime

import bcrypt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from sgde_server.auth.exceptions import EmailTaken, UsernameTaken, UserNotFound, InvalidToken, LoginRequired, \
    InvalidCredentials
from sgde_server.auth.schemas import UserCreate, JWTData, Token, UserDB
from sgde_server.config import settings
from sgde_server.database import UserTable, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_user_by_username(db: Session, username: str) -> UserDB | None:
    return db.query(UserTable).filter_by(username=username).first()


def get_user_by_username_required(db: Session, username: str) -> UserDB:
    user = get_user_by_username(db, username)
    if not user:
        raise UserNotFound()
    return user


def get_user_by_email(db: Session, email: str) -> UserDB | None:
    return db.query(UserTable).filter_by(email=email).first()


def get_users(db: Session, skip: int = 0, limit: int = 10) -> list[UserDB]:
    return db.query(UserTable).offset(skip).limit(limit).all()


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    b_plain_password = plain_password.encode()
    return bcrypt.checkpw(b_plain_password, hashed_password)


def get_password_hash(password: str) -> bytes:
    b_password = password.encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(b_password, salt)
    return hashed


def create_user(db: Session, user: UserCreate) -> UserDB:
    if get_user_by_username(db, user.username):
        raise UsernameTaken()
    if get_user_by_email(db, user.email):
        raise EmailTaken()
    hashed_password = get_password_hash(user.password)
    db_user = UserTable(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_access_token(user: UserDB, expires_delta: timedelta = timedelta(minutes=settings.JWT_EXP)):
    jwt_data = {
        "sub": user.username,
        "exp": datetime.utcnow() + expires_delta
    }
    return jwt.encode(jwt_data, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def parse_jwt_user_data(token: str = Depends(oauth2_scheme)) -> JWTData | None:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError:
        raise InvalidToken()
    return JWTData(**payload)


def parse_jwt_user_data_required(token: JWTData | None = Depends(parse_jwt_user_data)) -> JWTData:
    if not token:
        raise LoginRequired()
    return token


def authenticate_user(db: Session, username: str, password: str) -> UserDB:
    user = get_user_by_username(db, username)
    if not user:
        raise InvalidCredentials()
    if not verify_password(password, user.hashed_password):
        raise InvalidCredentials()
    return user


def create_access_token_for_auth_user(db: Session, username: str, password: str) -> Token:
    user = authenticate_user(db, username, password)
    access_token = create_access_token(user)
    return Token(access_token=access_token)


def get_current_user(db: Session = Depends(get_db), token: JWTData = Depends(parse_jwt_user_data_required)) -> UserDB:
    return get_user_by_username_required(db=db, username=token.username)
