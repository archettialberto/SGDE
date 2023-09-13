from fastapi import APIRouter, Query, Depends, UploadFile, File
from sqlalchemy.orm import Session
from starlette import status

from sgde_api.auth.utils import get_current_user, parse_jwt_user_data_required, JWTData
from sgde_api.database import get_db
from schemas import GeneratorCreate, Generator, User
from sgde_api.exchange.utils import (
    get_generator_by_name_required,
    create_generator,
    download_generator,
    get_generators,
)

router = APIRouter()


@router.get("/generators/", response_model=list[Generator])
def exchange_get_generators(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10),
    db: Session = Depends(get_db),
):
    return get_generators(db=db, skip=skip, limit=limit)


@router.get("/generators/{name}", response_model=Generator)
def exchange_get_generator(name: str = Query(), db: Session = Depends(get_db)):
    return get_generator_by_name_required(db=db, name=name)


@router.post(
    "/exchange/upload", status_code=status.HTTP_201_CREATED, response_model=Generator
)
def exchange_generator_upload(
    generator: GeneratorCreate = Depends(GeneratorCreate.as_form),
    current_user: User = Depends(get_current_user),
    onnx_file: UploadFile = File(),
    db: Session = Depends(get_db),
):
    return create_generator(
        db=db, generator=generator, username=current_user.username, onnx_file=onnx_file
    )


@router.get("/generators/{name}/download", response_model=Generator)
def exchange_generator_download(
    name: str = Query(),
    _: JWTData = Depends(parse_jwt_user_data_required),
    db: Session = Depends(get_db),
):
    return download_generator(db=db, name=name)
