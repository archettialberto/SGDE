from datetime import datetime

from sqlalchemy.orm import Session

from sgde_api_legacy.database import db_schemas, db_app
from sgde_api_legacy.security import oauth_utils


def get_user_by_username(db: Session, username: str):
    return db.query(db_app.User).filter(db_app.User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(db_app.User).filter(db_app.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_app.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: db_schemas.UserCreate):
    hashed_password = oauth_utils.get_password_hash(user.password)
    db_user = db_app.User(
        username=user.username,
        email=user.email,
        created=datetime.utcnow(),
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_generator_by_name(db: Session, name: str):
    return db.query(db_app.Generator).filter(db_app.Generator.name == name).first()


def get_generators(db: Session, skip: int = 0, limit: int = 100):
    return db.query(db_app.Generator).offset(skip).limit(limit).all()


def create_generator(db: Session, generator: db_schemas.GeneratorCreate, username: str, path: str):
    db_generator = db_app.Generator(
        **generator.dict(),
        owner=username,
        path=path,
        created=datetime.utcnow()
    )
    db.add(db_generator)
    db.commit()
    db.refresh(db_generator)
    return db_generator
