from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    LargeBinary,
    ForeignKey,
    Float,
    Boolean,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from sgde_api.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    Returns a database session, closing it when the context is exited.
    :return:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserTable(Base):
    """
    Database table for the SGDE API users.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(LargeBinary)

    generators_rel = relationship("GeneratorTable", back_populates="owner_rel")


class GeneratorTable(Base):
    """
    Database table for the SGDE API generators.
    """

    __tablename__ = "generators"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, index=True, nullable=False)

    data_name = Column(String, index=True)
    data_description = Column(String)
    data_structure = Column(String, index=True)
    data_length = Column(Integer, index=True)

    task = Column(String, index=True)

    metric = Column(String, index=True)
    best_score = Column(Float, index=True)
    best_score_real = Column(Float, index=True)

    gen_onnx_file = Column(String, index=True, nullable=False)
    cls_onnx_file = Column(String, index=True, nullable=True)
    json_file = Column(String, index=True, nullable=False)

    has_cls = Column(Boolean, index=True, nullable=False)

    owner = Column(String, ForeignKey("users.username"))

    owner_rel = relationship("UserTable", back_populates="generators_rel")
