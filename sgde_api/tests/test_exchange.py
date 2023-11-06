from starlette import status

from sgde_api.auth.exceptions import LoginRequired
from sgde_api.exchange.exceptions import (
    GeneratorNotFound,
    GeneratorExists,
    InvalidONNXError,
    InvalidJSONError,
)
from sgde_api.tests.conftest import foobar, register_and_login, foo_gan


def test_get_empty_generators(client):
    response = client.get("/generators")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_non_existent_generator(client):
    response = client.get("/generators/foo_gan")
    assert response.status_code == GeneratorNotFound.STATUS_CODE
    assert response.json()["detail"] == GeneratorNotFound.DETAIL


def test_upload_generator_no_cls(client, onnx_file, json_file):
    token = register_and_login(client)
    files = {
        "gen_onnx_file": onnx_file.well_formatted,
        "json_file": json_file.well_formatted,
    }
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == status.HTTP_201_CREATED
    _foo_gan = foo_gan.copy()
    _foo_gan["owner"] = foobar["username"]
    _foo_gan["has_cls"] = False
    assert response.json() == _foo_gan


def test_upload_generator_cls(client, onnx_file, json_file):
    token = register_and_login(client)
    files = {
        "gen_onnx_file": onnx_file.well_formatted,
        "cls_onnx_file": onnx_file.well_formatted,
        "json_file": json_file.well_formatted,
    }
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == status.HTTP_201_CREATED
    _foo_gan = foo_gan.copy()
    _foo_gan["owner"] = foobar["username"]
    _foo_gan["has_cls"] = True
    assert response.json() == _foo_gan


def test_upload_generator_no_token(client, onnx_file, json_file):
    files = {
        "gen_onnx_file": onnx_file.well_formatted,
        "json_file": json_file.well_formatted,
    }
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": "Bearer "},
        files=files,
    )
    assert response.status_code == LoginRequired.STATUS_CODE
    assert response.json()["detail"] == LoginRequired.DETAIL


def test_upload_generator_same_name(client, onnx_file, json_file):
    token = register_and_login(client)
    files = {
        "gen_onnx_file": onnx_file.well_formatted,
        "json_file": json_file.well_formatted,
    }
    client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == GeneratorExists.STATUS_CODE
    assert response.json()["detail"] == GeneratorExists.DETAIL


def test_upload_generator_corrupted_gen_onnx(client, onnx_file, json_file):
    token = register_and_login(client)
    files = {
        "gen_onnx_file": onnx_file.corrupted,
        "cls_onnx_file": onnx_file.well_formatted,
        "json_file": json_file.well_formatted,
    }
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == InvalidONNXError.STATUS_CODE
    assert response.json()["detail"] == InvalidONNXError.DETAIL


def test_upload_generator_corrupted_cls_onnx(client, onnx_file, json_file):
    token = register_and_login(client)
    files = {
        "gen_onnx_file": onnx_file.well_formatted,
        "cls_onnx_file": onnx_file.corrupted,
        "json_file": json_file.well_formatted,
    }
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == InvalidONNXError.STATUS_CODE
    assert response.json()["detail"] == InvalidONNXError.DETAIL


def test_upload_generator_corrupted_json(client, onnx_file, json_file):
    token = register_and_login(client)
    files = {
        "gen_onnx_file": onnx_file.well_formatted,
        "json_file": json_file.corrupted,
    }
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    assert response.status_code == InvalidJSONError.STATUS_CODE
    assert response.json()["detail"] == InvalidJSONError.DETAIL


def test_get_existent_generator_cls(client, onnx_file, json_file):
    token = register_and_login(client)
    files = {
        "gen_onnx_file": onnx_file.well_formatted,
        "cls_onnx_file": onnx_file.well_formatted,
        "json_file": json_file.well_formatted,
    }
    client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    response = client.get(f"/generators/{foo_gan['name']}")
    assert response.status_code == status.HTTP_200_OK
    _foo_gan = foo_gan.copy()
    _foo_gan["owner"] = foobar["username"]
    _foo_gan["has_cls"] = True
    assert response.json() == _foo_gan


def test_download_generator(client, onnx_file, json_file):
    token = register_and_login(client)
    files = {
        "gen_onnx_file": onnx_file.well_formatted,
        "json_file": json_file.well_formatted,
    }
    client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
    )
    response = client.get(
        "generators/foo_gan/download", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK


def test_download_non_existent_generator(client):
    token = register_and_login(client)
    response = client.get(
        "generators/foo_gan/download", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Generator not found"


def test_download_non_existent_generator_no_login(client):
    client.post("/auth/register", json=foobar)
    response = client.get(
        "generators/foo_gan/download", headers={"Authorization": "Bearer "}
    )
    assert response.status_code == LoginRequired.STATUS_CODE
    assert response.json()["detail"] == LoginRequired.DETAIL
