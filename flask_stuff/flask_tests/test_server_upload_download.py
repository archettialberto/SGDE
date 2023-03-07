import os
import shutil
from pathlib import Path

import pytest
from onnx import TensorProto
from onnx.checker import check_model
from onnx.helper import make_tensor_value_info, make_node, make_model, make_graph

from falsk_sgde_server.exceptions import APIException, MissingFieldException, InvalidFormatException, DoesNotExistException, \
    AlreadyExistsException
from falsk_sgde_server import create_app


@pytest.fixture()
def app():
    app = create_app(instance_path=Path(os.getcwd(), "test_instance"))
    app.config.update({"TESTING": True})
    yield app
    shutil.rmtree(app.instance_path)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def onnx_model() -> str:
    X = make_tensor_value_info('X', TensorProto.FLOAT, [None, None])
    A = make_tensor_value_info('A', TensorProto.FLOAT, [None, None])
    B = make_tensor_value_info('B', TensorProto.FLOAT, [None, None])
    Y = make_tensor_value_info('Y', TensorProto.FLOAT, [None])
    node1 = make_node('MatMul', ['X', 'A'], ['XA'])
    node2 = make_node('Add', ['XA', 'B'], ['Y'])
    graph = make_graph([node1, node2], 'lr', [X, A, B], [Y])
    onnx_model = make_model(graph)
    check_model(onnx_model)
    return str(onnx_model)


def check_exception(resp, exception: APIException):
    assert resp.status_code == exception.status_code and resp.json["msg"] == exception.msg


def test_generator_upload(app, client, onnx_model):
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

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "non-existent task", "generator_name": "sample_generator",
                             "onnx": onnx_model})
    check_exception(resp, DoesNotExistException("task_name"))

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task", "generator_name": "sample_generator", "onnx": onnx_model})
    assert resp.status_code == 201

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task", "generator_name": "sample_generator", "onnx": onnx_model})
    check_exception(resp, AlreadyExistsException("task_name'+'generator_name"))


def test_generator_download(app, client, onnx_model):
    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201

    resp = client.post("/auth/login", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201
    token = resp.json["access_token"]

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task"})
    assert resp.status_code == 201

    resp = client.post("/exchange/generators/upload", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task", "generator_name": "sample_generator", "onnx": onnx_model})
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
    assert resp.status_code == 200 and resp.json["onnx"] == onnx_model
