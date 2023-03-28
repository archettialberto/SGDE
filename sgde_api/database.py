from sqlalchemy import (
    create_engine,
    Column,
    String,
    Integer,
    LargeBinary,
    Boolean,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from sgde_api.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserTable(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(LargeBinary)

    generators_rel = relationship("GeneratorTable", back_populates="owner_rel")


class GeneratorTable(Base):
    __tablename__ = "generators"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    dataset_name = Column(String, index=True)
    dataset_description = Column(String)
    format = Column(String, index=True, nullable=False)
    image_size = Column(Integer, index=True)
    conditioned = Column(Boolean, index=True, nullable=False)
    task = Column(String, index=True)
    num_classes = Column(Integer, index=True)
    model_size = Column(String, index=True, nullable=False)
    generator_epochs = Column(Integer, index=True, nullable=False)
    generator_batch_size = Column(Integer, index=True, nullable=False)
    classifier_epochs = Column(Integer, index=True, nullable=False)
    classifier_batch_size = Column(Integer, index=True, nullable=False)
    discriminator_rounds = Column(Integer, index=True, nullable=False)
    generator_input_shape = Column(Integer, index=True, nullable=False)
    classifier_gen_best_accuracy = Column(Float, index=True, nullable=False)
    classifier_real_best_accuracy = Column(Float, index=True, nullable=False)
    ssim = Column(Float, index=True, nullable=False)
    avg_ssim = Column(Float, index=True, nullable=False)
    filename = Column(String, index=True, nullable=False)
    owner = Column(String, ForeignKey("users.username"))

    owner_rel = relationship("UserTable", back_populates="generators_rel")
