import os
import shutil
from pathlib import Path

import pytest

from sgde_server.exceptions import APIException, MissingFieldException, InvalidFormatException, DoesNotExistException, \
    AlreadyExistsException
from sgde_server import create_app


@pytest.fixture()
def app():
    app = create_app(instance_path=Path(os.getcwd(), "test_instance"))
    app.config.update({"TESTING": True})
    yield app
    shutil.rmtree(app.instance_path)


@pytest.fixture()
def client(app):
    return app.test_client()


def check_exception(resp, exception: APIException):
    assert resp.status_code == exception.status_code and resp.json["msg"] == exception.msg


def test_generator_upload(app, client):
    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201

    resp = client.post("/auth/login", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201
    token = resp.json["access_token"]

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task"})
    assert resp.status_code == 201

    resp = client.post("/exchange/generators/upload")
    assert resp.status_code == 401 and "Missing Authorization Header" == resp.json["msg"]

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"})
    check_exception(resp, MissingFieldException("task_name"))

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "t"})
    check_exception(resp, InvalidFormatException("task_name", InvalidFormatException.TOO_SHORT))

    long_task_name = 'foo' * app.config['MAX_TASK_NAME_LENGTH']
    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": f"{long_task_name}"})
    check_exception(resp, InvalidFormatException("task_name", InvalidFormatException.TOO_LONG))

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task"})
    check_exception(resp, MissingFieldException("generator_name"))

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task", "generator_name": "g"})
    check_exception(resp, InvalidFormatException("generator_name", InvalidFormatException.TOO_SHORT))

    long_generator_name = 'foo' * app.config['MAX_GENERATOR_NAME_LENGTH']
    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task", "generator_name": f"{long_generator_name}"})
    check_exception(resp, InvalidFormatException("generator_name", InvalidFormatException.TOO_LONG))

    with open("sample_model.onnx", "r") as f:
        onnx_data = f.read()

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "non-existent task", "generator_name": "sample_generator", "onnx": onnx_data})
    check_exception(resp, DoesNotExistException("task_name"))

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task", "generator_name": "sample_generator", "onnx": onnx_data})
    assert resp.status_code == 201

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task", "generator_name": "sample_generator", "onnx": onnx_data})
    check_exception(resp, AlreadyExistsException("task_name'+'generator_name"))


def test_generator_download(app, client):
    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201

    resp = client.post("/auth/login", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201
    token = resp.json["access_token"]

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task"})
    assert resp.status_code == 201

    with open("sample_model.onnx", "r") as f:
        onnx_data = f.read()

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task", "generator_name": "sample_generator", "onnx": onnx_data})
    assert resp.status_code == 201

    resp = client.get("/exchange/generators/download")
    assert resp.status_code == 401 and "Missing Authorization Header" == resp.json["msg"]

    resp = client.get("/exchange/generators/download", headers={"Authorization": f"Bearer {token}"})
    check_exception(resp, MissingFieldException("task_name"))

    resp = client.get("/exchange/generators/download", headers={"Authorization": f"Bearer {token}"},
                      data={"task_name": "t"})
    check_exception(resp, InvalidFormatException("task_name", InvalidFormatException.TOO_SHORT))

    long_task_name = 'foo' * app.config['MAX_TASK_NAME_LENGTH']
    resp = client.get("/exchange/generators/download", headers={"Authorization": f"Bearer {token}"},
                      data={"task_name": f"{long_task_name}"})
    check_exception(resp, InvalidFormatException("task_name", InvalidFormatException.TOO_LONG))

    resp = client.get("/exchange/generators/download", headers={"Authorization": f"Bearer {token}"},
                      data={"task_name": "sample_task"})
    check_exception(resp, MissingFieldException("generator_name"))

    resp = client.get("/exchange/generators/download", headers={"Authorization": f"Bearer {token}"},
                      data={"task_name": "sample_task", "generator_name": "g"})
    check_exception(resp, InvalidFormatException("generator_name", InvalidFormatException.TOO_SHORT))

    long_generator_name = 'foo' * app.config['MAX_GENERATOR_NAME_LENGTH']
    resp = client.get("/exchange/generators/download", headers={"Authorization": f"Bearer {token}"},
                      data={"task_name": "sample_task", "generator_name": f"{long_generator_name}"})
    check_exception(resp, InvalidFormatException("generator_name", InvalidFormatException.TOO_LONG))

    resp = client.get("/exchange/generators/download", headers={"Authorization": f"Bearer {token}"},
                      data={"task_name": "non-existent task", "generator_name": "sample_generator"})
    check_exception(resp, DoesNotExistException("task_name"))

    resp = client.get("/exchange/generators/download", headers={"Authorization": f"Bearer {token}"},
                      data={"task_name": "sample_task", "generator_name": "non-existent generator"})
    check_exception(resp, DoesNotExistException("task_name'+'generator_name"))

    resp = client.get("/exchange/generators/download", headers={"Authorization": f"Bearer {token}"},
                      data={"task_name": "sample_task", "generator_name": "sample_generator"})
    assert resp.status_code == 200 and resp.json["onnx"] == onnx_data