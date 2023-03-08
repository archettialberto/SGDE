from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from sgde_server.auth.schemas import User, UserCreate, JWTData, Token
from sgde_server.auth.utils import get_users, create_user, get_user_by_username_required, parse_jwt_user_data_required, \
    create_access_token_for_auth_user
from sgde_server.database import get_db

router = APIRouter()


@router.get("/users/", response_model=list[User])
def auth_get_users(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10),
        db: Session = Depends(get_db)
):
    return get_users(db=db, skip=skip, limit=limit)


@router.get("/users/{username}", response_model=User)
def auth_get_user(
        username: str,
        db: Session = Depends(get_db)
):
    return get_user_by_username_required(db=db, username=username)


@router.post("/auth/register", status_code=status.HTTP_201_CREATED, response_model=User)
def auth_register(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    return create_user(db=db, user=user)


@router.post("/auth/token", response_model=Token)
def auth_token(
        auth_form: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    return create_access_token_for_auth_user(db=db, username=auth_form.username, password=auth_form.password)


@router.get("/auth/whoami", response_model=User)
def auth_whoami(
        jwt_data: JWTData = Depends(parse_jwt_user_data_required),
        db: Session = Depends(get_db)
):
    return get_user_by_username_required(db=db, username=jwt_data.username)
