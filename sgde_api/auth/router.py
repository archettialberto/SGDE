from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

from sgde_utils.schemas import UserCreate, User
from sgde_api.auth.utils import (
    get_users,
    create_user,
    get_user_by_username_required,
    parse_jwt_user_data_required,
    create_access_token_for_auth_user,
    JWTData,
    Token,
)
from sgde_api.database import get_db

router = APIRouter()


@router.get("/users/", response_model=list[User])
def auth_get_users(
    db: Session = Depends(get_db),
):
    """
    Returns the list of all registered users.
    """
    return get_users(db=db)


@router.get("/users/{username}", response_model=User)
def auth_get_user(username: str, db: Session = Depends(get_db)):
    """
    Returns the data of a specific user.
    """
    return get_user_by_username_required(db=db, username=username)


@router.post("/auth/register", status_code=status.HTTP_201_CREATED, response_model=User)
def auth_register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user.
    """
    return create_user(db=db, user=user)


@router.post("/auth/token", response_model=Token)
def auth_token(
    auth_form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Returns an access token for a specific user.
    """
    return create_access_token_for_auth_user(
        db=db, username=auth_form.username, password=auth_form.password
    )


@router.get("/auth/whoami", response_model=User)
def auth_whoami(
    jwt_data: JWTData = Depends(parse_jwt_user_data_required),
    db: Session = Depends(get_db),
):
    """
    Returns the current logged user.
    """
    return get_user_by_username_required(db=db, username=jwt_data.username)
