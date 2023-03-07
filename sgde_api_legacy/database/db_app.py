from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

from sgde_api_legacy.settings import get_settings

engine = create_engine(get_settings().sgde_sqlalchemy_database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created = Column(String, index=True)

    generators_rel = relationship("Generator", back_populates="owner_rel")


class Generator(Base):
    __tablename__ = "generators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    conditioned = Column(Boolean, index=True)
    data_format = Column(String, index=True)
    task = Column(String, index=True)
    num_classes = Column(Integer, index=True)
    model_size = Column(String, index=True)
    epochs = Column(Integer, index=True)
    batch_size = Column(Integer, index=True)
    description = Column(String)
    path = Column(String, index=True)
    created = Column(String, index=True)
    owner = Column(String, ForeignKey("users.username"))

    owner_rel = relationship("User", back_populates="generators_rel")
