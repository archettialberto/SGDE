import json
import os
import tempfile
import uuid
import zipfile

import onnx
from fastapi import UploadFile
from sqlalchemy.orm import Session
from starlette.responses import FileResponse

from sgde_api.config import settings
from sgde_api.database import GeneratorTable
from sgde_api.exceptions import InternalServerError
from sgde_api.exchange.exceptions import (
    GeneratorNotFound,
    GeneratorExists,
    InvalidONNXError,
    FileWritingError,
    InvalidJSONError,
)
from sgde_utils.schemas import GeneratorExtended, Generator


class GeneratorDB(Generator):
    """
    Class for the database representation of a generator.
    """

    gen_onnx_file: str
    cls_onnx_file: str | None
    json_file: str
    has_cls: bool


def get_generator_by_name(db: Session, name: str) -> GeneratorDB | None:
    """
    Get a generator by its name. If it does not exist, return None.
    :param db: database session
    :param name: name of the generator
    :return: a single GeneratorDB object or None
    """
    return db.query(GeneratorTable).filter_by(name=name).first()


def get_generator_by_name_required(db: Session, name: str) -> GeneratorDB:
    """
    Get a generator by its name. If it does not exist, raise an exception.
    :param db: database session
    :param name: name of the generator
    :return: a single GeneratorDB object
    """
    generator = get_generator_by_name(db, name)
    if not generator:
        raise GeneratorNotFound()
    return generator


def get_generators(db: Session) -> list[GeneratorDB]:
    """
    Get a list of generators.
    :param db: database session
    :return: a list of GeneratorDB objects
    """
    return db.query(GeneratorTable).offset(0).all()


def save_generator_file(generator_name: str, upload_file: UploadFile) -> str:
    """
    Save a generator's ONNX file on the server.
    :param generator_name: name of the generator
    :param upload_file: UploadFile object containing the generator's ONNX file
    """

    filename = f"{generator_name}_{uuid.uuid4()}.onnx"
    try:
        contents = upload_file.file.read()
        onnx.checker.check_model(contents)
        with open(os.path.join(settings.GENERATOR_PATH, filename), "wb") as f:
            f.write(contents)

    except onnx.checker.ValidationError as exc:
        raise InvalidONNXError() from exc
    except Exception as exc:
        raise FileWritingError() from exc
    finally:
        upload_file.file.close()
    return filename


def create_generator(
    db: Session,
    username: str,
    gen_onnx_file: UploadFile,
    cls_onnx_file: UploadFile,
    json_file: UploadFile,
) -> GeneratorDB:
    """
    Create a new generator on the server.
    :param db: database session
    :param username: username of the generator's owner
    :param gen_onnx_file: ONNX file of the generator
    :param cls_onnx_file: ONNX file of the classifier
    :param json_file: JSON file of the generator
    :return: the created GeneratorDB object
    """
    try:
        model_dict = json.loads(json_file.file.read())
        generator_create = GeneratorExtended(**model_dict)
    except json.JSONDecodeError as exc:
        raise InvalidJSONError from exc
    except ValueError as exc:
        raise InvalidJSONError from exc

    if get_generator_by_name(db, generator_create.name):
        raise GeneratorExists()

    json_file_name = f"{generator_create.name}_{uuid.uuid4()}.json"
    with open(os.path.join(settings.GENERATOR_PATH, json_file_name), "w") as f:
        json.dump(generator_create.dict(), f, indent=2)

    gen_onnx_file_path = save_generator_file(generator_create.name, gen_onnx_file)
    cls_onnx_file_path = (
        save_generator_file(generator_create.name, cls_onnx_file)
        if cls_onnx_file
        else None
    )

    db_generator = GeneratorDB(
        **generator_create.dict(),
        owner=username,
        gen_onnx_file=gen_onnx_file_path,
        cls_onnx_file=cls_onnx_file_path,
        json_file=json_file_name,
        has_cls=cls_onnx_file is not None,
    )
    db_generator = GeneratorTable(**db_generator.dict())
    db.add(db_generator)
    db.commit()
    db.refresh(db_generator)
    return db_generator


def download_generator(db: Session, name: str) -> FileResponse:
    """
    Download a generator's ONNX and JSON files from the server.
    :param db: database session
    :param name: name of the generator
    :return: FileResponse zip containing the generator's ONNX and JSON files
    """
    generator = get_generator_by_name_required(db, name)
    gen_onnx_path = os.path.join(settings.GENERATOR_PATH, generator.gen_onnx_file)
    json_path = os.path.join(settings.GENERATOR_PATH, generator.json_file)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
        try:
            with zipfile.ZipFile(temp_zip.name, "w") as zipf:
                zipf.write(
                    gen_onnx_path, f"{generator.owner}_{generator.name}_gen.onnx"
                )
                if generator.cls_onnx_file:
                    cls_onnx_path = os.path.join(
                        settings.GENERATOR_PATH, generator.cls_onnx_file
                    )
                    zipf.write(
                        cls_onnx_path, f"{generator.owner}_{generator.name}_cls.onnx"
                    )
                zipf.write(json_path, f"{generator.owner}_{generator.name}.json")
            response = FileResponse(
                temp_zip.name, filename=f"{generator.owner}_{generator.name}.zip"
            )
        except Exception as exc:
            os.unlink(temp_zip.name)
            raise InternalServerError() from exc

    def delete_temp_file():
        os.unlink(temp_zip.name)

    response.on_send = delete_temp_file

    return response
