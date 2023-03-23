from starlette import status

from sgde_api.auth.exceptions import LoginRequired
from sgde_api.exchange.exceptions import GeneratorNotFound, GeneratorExists, InvalidONNX
from schemas import GENERATOR_NAME_PATTERN, DataFormat, Task, ModelSize

foobar = {"username": "foobar", "email": "user@example.com", "password": "aaaAAA1!"}

foo_gan = {
    "name": "foo_gan",
    "conditioned": False,
    "data_format": DataFormat.image.value,
    "task": Task.classification.value,
    "num_classes": 2,
    "model_size": ModelSize.small.value,
    "epochs": 1,
    "batch_size": 1,
    "description": "My awesome FooGAN",
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
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_201_CREATED
    _foo_gan = foo_gan.copy()
    _foo_gan["owner"] = foobar["username"]
    assert response.json() == _foo_gan


def test_upload_generator_same_name(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=foo_gan,
        files=files,
    )
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=foo_gan,
        files=files,
    )
    assert response.status_code == GeneratorExists.STATUS_CODE
    assert response.json()["detail"] == GeneratorExists.DETAIL


def test_upload_generator_corrupted_onnx(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.corrupted}
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=foo_gan,
        files=files,
    )
    assert response.status_code == InvalidONNX.STATUS_CODE
    assert response.json()["detail"] == InvalidONNX.DETAIL


def test_upload_generator_no_token(client, onnx_file):
    files = {"onnx_file": onnx_file.well_formatted}
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": "Bearer "},
        data=foo_gan,
        files=files,
    )
    assert response.status_code == LoginRequired.STATUS_CODE
    assert response.json()["detail"] == LoginRequired.DETAIL


def test_get_existent_generator(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=foo_gan,
        files=files,
    )
    response = client.get(f"/generators/{foo_gan['name']}")
    assert response.status_code == status.HTTP_200_OK
    _foo_gan = foo_gan.copy()
    _foo_gan["owner"] = foobar["username"]
    assert response.json() == _foo_gan


def test_get_non_empty_generators(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    expected_resp = []
    for i in range(15):
        files = {"onnx_file": onnx_file.well_formatted}
        _foo_gan = foo_gan.copy()
        _foo_gan["name"] = f"my_gan{i}"
        client.post(
            "/exchange/upload",
            headers={"Authorization": f"Bearer {token}"},
            data=_foo_gan,
            files=files,
        )
        _foo_gan["owner"] = foobar["username"]
        expected_resp.append(_foo_gan)
    response = client.get("/generators?skip=3&limit=100")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected_resp[3:]


def test_upload_generator_wrong_name(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["name"] = "bad gan"
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == f'string does not match regex "{GENERATOR_NAME_PATTERN.pattern}"'
    )


def test_upload_generator_wrong_conditioned(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["conditioned"] = "t r u e"
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"] == "value could not be parsed to a boolean"
    )


def test_upload_generator_wrong_data_format(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["data_format"] = "time_series"
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == "value is not a valid enumeration member; "
        "permitted: 'image', 'tabular'"
    )


def test_upload_generator_wrong_task(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["task"] = "segmentation"
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == "value is not a valid enumeration member; "
        "permitted: 'classification', 'regression'"
    )


def test_upload_generator_wrong_num_classes(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["num_classes"] = 1
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == "ensure this value is greater than or equal to 2"
    )


def test_upload_generator_wrong_model_size(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["model_size"] = "curvy"
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == "value is not a valid enumeration member; "
        "permitted: 'small', 'medium', 'large'"
    )


def test_upload_generator_wrong_epochs(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["epochs"] = 0
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == "ensure this value is greater than or equal to 1"
    )


def test_upload_generator_wrong_batch_size(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["batch_size"] = 0
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == "ensure this value is greater than or equal to 1"
    )


def test_upload_generator_wrong_description(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    _foo_gan = foo_gan.copy()
    _foo_gan["description"] = "x"
    response = client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=_foo_gan,
        files=files,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert (
        response.json()["detail"][0]["msg"]
        == "ensure this value has at least 4 characters"
    )


def test_download_generator(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    files = {"onnx_file": onnx_file.well_formatted}
    client.post(
        "/exchange/upload",
        headers={"Authorization": f"Bearer {token}"},
        data=foo_gan,
        files=files,
    )
    response = client.get(
        "generators/foo_gan/download", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.read() == onnx_file.well_formatted


def test_download_non_existent_generator(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    response = client.get(
        "generators/foo_gan/download", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Generator not found"


def test_download_non_existent_generator_no_login(client, onnx_file):
    client.post("/auth/register", json=foobar)
    response = client.get(
        "generators/foo_gan/download", headers={"Authorization": f"Bearer "}
    )
    assert response.status_code == LoginRequired.STATUS_CODE
    assert response.json()["detail"] == LoginRequired.DETAIL
