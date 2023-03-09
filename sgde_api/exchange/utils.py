import os
import uuid

import onnx
from fastapi import UploadFile
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from sgde_api.config import settings
from sgde_api.database import GeneratorTable
from sgde_api.exchange.exceptions import GeneratorNotFound, GeneratorExists, InvalidONNX, FileWritingError
from sgde_api.exchange.schemas import GeneratorCreate, GeneratorDB


def get_generator_by_name(db: Session, name: str) -> GeneratorDB | None:
    return db.query(GeneratorTable).filter_by(name=name).first()


def get_generator_by_name_required(db: Session, name: str) -> GeneratorDB:
    generator = get_generator_by_name(db, name)
    if not generator:
        raise GeneratorNotFound()
    return generator


def get_generators(db: Session, skip: int = 0, limit: int = 10) -> list[GeneratorDB]:
    return db.query(GeneratorTable).offset(skip).limit(limit).all()


def save_generator_file(onnx_file: UploadFile) -> str:
    filename = f"{uuid.uuid4()}.onnx"
    try:
        contents = onnx_file.file.read()
        onnx.checker.check_model(contents)
        with open(os.path.join(settings.GENERATOR_PATH, filename), 'wb') as f:
            f.write(contents)
    except onnx.checker.ValidationError:
        raise InvalidONNX()
    except Exception:
        raise FileWritingError()
    finally:
        onnx_file.file.close()
    return filename


def create_generator(db: Session, generator: GeneratorCreate, username: str, onnx_file: UploadFile) -> GeneratorDB:
    if get_generator_by_name(db, generator.name):
        raise GeneratorExists()
    filename = save_generator_file(onnx_file)
    db_generator = GeneratorTable(
        **generator.dict(),
        owner=username,
        filename=filename,
    )
    db.add(db_generator)
    db.commit()
    db.refresh(db_generator)
    return db_generator


def download_generator(db: Session, name: str) -> FileResponse:
    generator = get_generator_by_name_required(db, name)
    generator_path = os.path.join(settings.GENERATOR_PATH, generator.filename)
    return FileResponse(path=generator_path, filename=f"{generator.owner}_{generator.name}.onnx")
