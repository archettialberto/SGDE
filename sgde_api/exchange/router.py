from fastapi import APIRouter, Query, Depends, UploadFile, File
from sqlalchemy.orm import Session
from starlette import status

from sgde_api.auth.utils import get_current_user, parse_jwt_user_data_required, JWTData
from sgde_api.database import get_db
from sgde_utils.schemas import Generator, User
from sgde_api.exchange.utils import (
    get_generator_by_name_required,
    create_generator,
    download_generator,
    get_generators,
)

router = APIRouter()


@router.get("/generators/", response_model=list[Generator])
def exchange_get_generators(
    db: Session = Depends(get_db),
):
    """
    Returns the list of all the available generators.
    """
    return get_generators(db=db)


@router.get("/generators/{name}", response_model=Generator)
def exchange_get_generator(name: str = Query(), db: Session = Depends(get_db)):
    """
    Returns the metadata of a specific generator.
    """
    return get_generator_by_name_required(db=db, name=name)


@router.post(
    "/exchange/upload", status_code=status.HTTP_201_CREATED, response_model=Generator
)
def exchange_generator_upload(
    current_user: User = Depends(get_current_user),
    gen_onnx_file: UploadFile = File(),
    cls_onnx_file: UploadFile = File(default=None),
    json_file: UploadFile = File(),
    db: Session = Depends(get_db),
):
    """
    Uploads a new generator to the server.
    """
    return create_generator(
        db=db,
        username=current_user.username,
        gen_onnx_file=gen_onnx_file,
        cls_onnx_file=cls_onnx_file,
        json_file=json_file,
    )


@router.get("/generators/{name}/download", response_model=Generator)
def exchange_generator_download(
    name: str = Query(),
    _: JWTData = Depends(parse_jwt_user_data_required),
    db: Session = Depends(get_db),
):
    """
    Downloads the ONNX and JSON files of a generator.
    """
    return download_generator(db=db, name=name)
