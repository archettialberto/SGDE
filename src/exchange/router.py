from fastapi import APIRouter, Query, Depends, Form, UploadFile, File
from sqlalchemy.orm import Session
from starlette import status

from src.auth.schemas import User, JWTData
from src.auth.utils import get_current_user, parse_jwt_user_data_required
from src.database import get_db
from src.exchange.schemas import Generator, DataFormat, Task, ModelSize, GeneratorCreate
from src.exchange.utils import get_generator_by_name_required, create_generator, download_generator, get_generators

router = APIRouter()


@router.get("/generators/", response_model=list[Generator])
def exchange_get_generators(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10),
        db: Session = Depends(get_db)
):
    return get_generators(db=db, skip=skip, limit=limit)


@router.get("/generators/{name}", response_model=Generator)
def exchange_get_generator(
        name: str = Query(),
        db: Session = Depends(get_db)
):
    return get_generator_by_name_required(db=db, name=name)


@router.post("/exchange/upload", status_code=status.HTTP_201_CREATED, response_model=Generator)
def exchange_generator_upload(
        name: str = Form(),
        conditioned: bool = Form(),
        data_format: DataFormat = Form(),
        task: Task | None = Form(default=None),
        num_classes: int | None = Form(default=None, ge=2),
        model_size: ModelSize = Form(),
        epochs: int = Form(ge=1),
        batch_size: int = Form(ge=1),
        description: str = Form(min_length=4),
        current_user: User = Depends(get_current_user),
        onnx_file: UploadFile = File(),
        db: Session = Depends(get_db)
):
    generator = GeneratorCreate(
        name=name,
        conditioned=conditioned,
        data_format=data_format,
        task=task,
        num_classes=num_classes,
        model_size=model_size,
        epochs=epochs,
        batch_size=batch_size,
        description=description
    )
    return create_generator(db=db, generator=generator, username=current_user.username, onnx_file=onnx_file)


@router.get("/generators/{name}/download", response_model=Generator)
def exchange_generator_download(
        name: str = Query(),
        _: JWTData = Depends(parse_jwt_user_data_required),
        db: Session = Depends(get_db)
):
    return download_generator(db=db, name=name)
