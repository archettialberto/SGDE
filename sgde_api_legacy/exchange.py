import os
import uuid
import onnx
from fastapi import HTTPException, Depends, Form, File, UploadFile, Path, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from sgde_api_legacy.settings import get_settings
from sgde_api_legacy.database import db_app, db_schemas, db_utils
from sgde_api_legacy.security import oauth_utils
from app import app


@app.post("/exchange/upload", response_model=db_schemas.Generator)
def exchange_upload(
        name: str = Form(**get_settings().sgde_generator_name_params),
        conditioned: bool = Form(),
        data_format: db_schemas.DataFormat = Form(),
        task: db_schemas.Task | None = Form(default=None),
        num_classes: int | None = Form(default=None, ge=2),
        model_size: db_schemas.ModelSize = Form(),
        epochs: int = Form(ge=1),
        batch_size: int = Form(ge=1),
        description: str = Form(**get_settings().sgde_generator_description_params),
        current_user: db_schemas.User = Depends(oauth_utils.get_current_user),
        onnx_file: UploadFile = File(),
        db: Session = Depends(db_app.get_db)
):
    db_generator = db_utils.get_generator_by_name(db, name=name)
    if db_generator:
        raise HTTPException(status_code=400, detail="Generator with the same name already exists")

    filename = f"{uuid.uuid4()}.onnx"
    try:
        contents = onnx_file.file.read()
        onnx.checker.check_model(contents)
        with open(os.path.join(get_settings().sgde_generator_path, filename), 'wb') as f:
            f.write(contents)
    except onnx.checker.ValidationError:
        raise HTTPException(status_code=400, detail="Invalid ONNX model")
    except Exception:
        raise HTTPException(status_code=400, detail="Error during file upload")
    finally:
        onnx_file.file.close()

    created_generator = db_utils.create_generator(
        db=db,
        generator=db_schemas.GeneratorCreate(**{
            "name": name,
            "conditioned": conditioned,
            "data_format": data_format,
            "task": task,
            "num_classes": num_classes,
            "model_size": model_size,
            "epochs": epochs,
            "batch_size": batch_size,
            "description": description,
        }),
        username=current_user.username,
        path=filename
    )
    return created_generator


@app.get("/exchange/download/{name}", response_model=db_schemas.Generator)
async def exchange_download(
        name: str = Path(**get_settings().sgde_generator_name_params),
        _: db_schemas.User = Depends(oauth_utils.get_current_user),
        db: Session = Depends(db_app.get_db),
):
    db_generator = db_utils.get_generator_by_name(db, name=name)
    if db_generator is None:
        raise HTTPException(status_code=404, detail="Generator not found")

    generator_path = os.path.join(get_settings().sgde_generator_path, db_generator.path)
    return FileResponse(path=generator_path, filename=f"{db_generator.owner}_{db_generator.name}.onnx")


@app.get("/generators", response_model=list[db_schemas.Generator])
async def get_generators(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, le=get_settings().sgde_max_items_from_get),
        db: Session = Depends(db_app.get_db)
):
    generators = db_utils.get_generators(db, skip=skip, limit=limit)
    return generators


@app.get("/generators/{name}", response_model=db_schemas.Generator)
async def get_generator(
        name: str,
        db: Session = Depends(db_app.get_db)
):
    db_generator = db_utils.get_generator_by_name(db, name=name)
    if db_generator is None:
        raise HTTPException(status_code=404, detail="Generator not found")
    return db_generator
