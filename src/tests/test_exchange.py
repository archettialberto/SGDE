from starlette import status

from src.auth.exceptions import LoginRequired
from src.exchange.exceptions import GeneratorNotFound, GeneratorExists, InvalidONNX
from src.exchange.schemas import DataFormat, Task, ModelSize

foobar = {
    "username": "foobar",
    "email": "user@example.com",
    "password": "aaaAAA1!"
}

foo_gan = {
    "name": "foo_gan",
    "conditioned": False,
    "data_format": DataFormat.image.value,
    "task": Task.classification.value,
    "num_classes": 2,
    "model_size": ModelSize.small.value,
    "epochs": 1,
    "batch_size": 1,
    "description": "My awesome FooGAN"
}


def test_get_empty_generators(client):
    response = client.get("/generators")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_non_existent_generator(client):
    response = client.get("/generators/foo_gan")
    assert response.status_code == GeneratorNotFound.STATUS_CODE
    assert response.json()["detail"] == GeneratorNotFound.DETAIL


def test_upload_generator(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post("/auth/token", data={"username": foobar["username"], "password": foobar["password"]})
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=foo_gan, files=files)
    assert response.status_code == status.HTTP_201_CREATED
    _foo_gan = foo_gan.copy()
    _foo_gan["owner"] = foobar["username"]
    assert response.json() == _foo_gan


def test_upload_generator_same_name(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post("/auth/token", data={"username": foobar["username"], "password": foobar["password"]})
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=foo_gan, files=files)
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=foo_gan, files=files)
    assert response.status_code == GeneratorExists.STATUS_CODE
    assert response.json()["detail"] == GeneratorExists.DETAIL


def test_upload_generator_corrupted_onnx(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post("/auth/token", data={"username": foobar["username"], "password": foobar["password"]})
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.corrupted}
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=foo_gan, files=files)
    assert response.status_code == InvalidONNX.STATUS_CODE
    assert response.json()["detail"] == InvalidONNX.DETAIL


def test_upload_generator_no_token(client, onnx_file):
    files = {"onnx_file": onnx_file.well_formatted}
    response = client.post("/exchange/upload", headers={"Authorization": "Bearer "}, data=foo_gan, files=files)
    assert response.status_code == LoginRequired.STATUS_CODE
    assert response.json()["detail"] == LoginRequired.DETAIL


def test_get_existent_generator(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post("/auth/token", data={"username": foobar["username"], "password": foobar["password"]})
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=foo_gan, files=files)
    response = client.get(f"/generators/{foo_gan['name']}")
    assert response.status_code == status.HTTP_200_OK
    _foo_gan = foo_gan.copy()
    _foo_gan["owner"] = foobar["username"]
    assert response.json() == _foo_gan


def test_get_non_empty_generators(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post("/auth/token", data={"username": foobar["username"], "password": foobar["password"]})
    token = response.json()["access_token"]
    expected_resp = []
    for i in range(15):
        files = {"onnx_file": onnx_file.well_formatted}
        _foo_gan = foo_gan.copy()
        _foo_gan["name"] = f"my_gan{i}"
        client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=_foo_gan, files=files)
        _foo_gan["owner"] = foobar["username"]
        expected_resp.append(_foo_gan)
    response = client.get("/generators?skip=3&limit=100")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_resp[3:]


def test_upload_generator_wrong_name(client, onnx_file):
    # TODO add tests for generator field validation
    # TODO test generator download
    client.post("/auth/register", json=foobar)
    response = client.post("/auth/token", data={"username": foobar["username"], "password": foobar["password"]})
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["name"] = "gan"
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=_foo_gan, files=files)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == _foo_gan
