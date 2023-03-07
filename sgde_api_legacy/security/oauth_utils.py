from datetime import timedelta, datetime

from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status

from sgde_api_legacy.settings import get_settings
from sgde_api_legacy.database import db_app, db_utils
from sgde_api_legacy.security.oauth_app import pwd_context, oauth2_scheme
from sgde_api_legacy.security.oauth_schemas import TokenData


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str):
    user = db_utils.get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, get_settings().sgde_secret_key, algorithm=get_settings().sgde_jwt_algorithm)
    return encoded_jwt


def get_current_user(db: Session = Depends(db_app.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, get_settings().sgde_secret_key, algorithms=[get_settings().sgde_jwt_algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db_utils.get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user
