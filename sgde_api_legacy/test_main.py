import os
import shutil

import pytest
from fastapi.testclient import TestClient
from onnx import TensorProto
from onnx.checker import check_model
from onnx.helper import make_tensor_value_info, make_node, make_graph, make_model

from sgde_api_legacy.settings import get_settings
from app import app


@pytest.fixture(scope="function")
def client():
    from sgde_api_legacy.database.db_app import Base, engine
    Base.metadata.create_all(bind=engine)

    yield TestClient(app)

    os.remove(os.path.join(get_settings().sgde_instance_path, get_settings().sgde_db_filename))
    # shutil.rmtree(os.path.join(get_settings().sgde_instance_path, get_settings().sgde_db_filename))


@pytest.fixture(scope="module")
def onnx_file():
    onnx_folder = os.path.join(os.getcwd(), "test_onnx")
    os.makedirs(onnx_folder, exist_ok=True)

    X = make_tensor_value_info('X', TensorProto.FLOAT, [None, None])
    A = make_tensor_value_info('A', TensorProto.FLOAT, [None, None])
    B = make_tensor_value_info('B', TensorProto.FLOAT, [None, None])
    Y = make_tensor_value_info('Y', TensorProto.FLOAT, [None])
    node1 = make_node('MatMul', ['X', 'A'], ['XA'])
    node2 = make_node('Add', ['XA', 'B'], ['Y'])
    graph = make_graph([node1, node2], 'lr', [X, A, B], [Y])
    onnx_model = make_model(graph)
    check_model(onnx_model)

    with open(os.path.join(onnx_folder, "onnx_model.onnx"), "wb") as f:
        f.write(onnx_model.SerializeToString())

    with open(os.path.join(onnx_folder, "wrong_onnx_model.onnx"), "w") as f:
        f.write(str(onnx_model))

    class ONNXFileBearer:
        def __init__(self):
            with open(os.path.join(onnx_folder, "onnx_model.onnx"), "rb") as f:
                self.well_formatted = f.read()

            with open(os.path.join(onnx_folder, "wrong_onnx_model.onnx"), "r") as f:
                self.corrupted = f.read()

    yield ONNXFileBearer()
    shutil.rmtree(onnx_folder)


def test_auth_register(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == []

    response = client.get("/auth/register")
    assert response.status_code == 405

    response = client.post("/auth/register")
    assert response.status_code == 422

    response = client.post("/auth/register", json={"username": "foo", "email": "user@example.com", "password": "aaaAAA1!"})
    assert response.status_code == 422

    response = client.post("/auth/register", json={"username": "foobar", "email": "userexample.com", "password": "aaaAAA1!"})
    assert response.status_code == 422

    response = client.post("/auth/register", json={"username": "foo+bar", "email": "user@example.com", "password": "aaaAAA11"})
    assert response.status_code == 422

    response = client.post("/auth/register", json={"username": "foobar", "email": "user@example.com", "password": "aaaAAA11"})
    assert response.status_code == 422

    response = client.post("/auth/register", json={"username": "foobar", "email": "user@example.com", "password": "aaaAAA1!"})
    assert response.status_code == 200
    created = response.json()["created"]

    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == [{"username": "foobar", "email": "user@example.com", "created": created}]

    response = client.post("/auth/register", json={"username": "foobar", "email": "user2@example.com", "password": "aaaAAA1!"})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Username already registered'}

    response = client.post("/auth/register", json={"username": "foobar2", "email": "user@example.com", "password": "aaaAAA1!"})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Email already registered'}


def test_auth_login(client):
    response = client.post("/auth/register", json={"username": "foobar", "email": "user@example.com", "password": "aaaAAA1!"})
    created = response.json()["created"]
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == [{"username": "foobar", "email": "user@example.com", "created": created}]

    response = client.get("/auth/login")
    assert response.status_code == 405

    response = client.post("/auth/login")
    assert response.status_code == 422

    response = client.post("/auth/login", data={"username": "foo", "password": "aaaAAA1!"})
    assert response.json() == {'detail': 'Incorrect username or password'}
    assert response.status_code == 401

    response = client.post("/auth/login", data={"username": "foobar", "password": "aaaAAA11"})
    assert response.status_code == 401

    response = client.post("/auth/login", data={"username": "foobar2", "password": "aaaAAA1!"})
    assert response.status_code == 401

    response = client.post("/auth/login", data={"username": "foobar", "password": "aaaAAA1!"})
    token = response.json()["access_token"]
    assert response.json() == {"access_token": token, "token_type": "bearer"}
    assert response.status_code == 200

    response = client.get("/auth/whoami", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == {"username": "foobar", "email": "user@example.com", "created": created}
    assert response.status_code == 200


def test_whoami(client):
    response = client.post("/auth/register", json={"username": "foobar", "email": "user@example.com", "password": "aaaAAA1!"})
    created = response.json()["created"]
    assert response.status_code == 200

    response = client.post("/auth/login", data={"username": "foobar", "password": "aaaAAA1!"})
    assert response.status_code == 200
    token = response.json()["access_token"]

    response = client.post("/auth/whoami")
    assert response.status_code == 405

    response = client.get("/auth/whoami")
    assert response.json() == {'detail': 'Not authenticated'}
    assert response.status_code == 401

    response = client.get("/auth/whoami", headers={"Authorization": f"Bearer {'.' + token[1:]}"})
    assert response.json() == {'detail': 'Could not validate credentials'}
    assert response.status_code == 401

    response = client.get("/auth/whoami", headers={"Authorization": f"Bearer {token}"})
    assert response.json() == {"username": "foobar", "email": "user@example.com", "created": created}
    assert response.status_code == 200


def test_get_users(client):
    response = client.post("/users")
    assert response.status_code == 405

    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == []

    created_list = []
    for i in range(25):
        response = client.post("/auth/register", json={"username": f"foobar{i}", "email": f"user{i}@example.com", "password": "aaaAAA1!"})
        assert response.status_code == 200
        created_list.append(response.json()["created"])

    response = client.get("/users?limit=25")
    assert response.status_code == 200
    assert response.json() == [
        {"username": f"foobar{i}", "email": f"user{i}@example.com", "created": created}
        for i, created in enumerate(created_list)
    ]

    response = client.get(f"/users?skip=0&limit=a")
    assert response.status_code == 422

    response = client.get(f"/users?skip=-1&limit=100")
    assert response.status_code == 422

    skip = 5
    limit = 10
    response = client.get(f"/users?skip={skip}&limit={limit}")
    assert response.status_code == 200
    assert response.json() == [
        {"username": f"foobar{i+skip}", "email": f"user{i+skip}@example.com", "created": created}
        for i, created in enumerate(created_list[skip:skip+limit])
    ]


def test_get_user(client):
    response = client.post("/users/foobar")
    assert response.status_code == 405

    response = client.get("/users/foobar")
    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}

    response = client.get("/users/foobar/foobar")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}

    response = client.post("/auth/register", json={"username": "foobar", "email": "user@example.com", "password": "aaaAAA1!"})
    assert response.status_code == 200
    created = response.json()["created"]

    response = client.get("/users/foobar")
    assert response.status_code == 200
    assert response.json() == {"username": "foobar", "email": "user@example.com", "created": created}


def test_exchange_upload(client, onnx_file):
    response = client.post("/auth/register", json={"username": "foobar", "email": "user@example.com", "password": "aaaAAA1!"})
    assert response.status_code == 200

    response = client.post("/auth/login", data={"username": "foobar", "password": "aaaAAA1!"})
    token = response.json()["access_token"]
    assert response.status_code == 200

    response = client.get("/exchange/upload")
    assert response.status_code == 405

    response = client.post("/exchange/upload")
    assert response.status_code == 401
    assert response.json() == {'detail': 'Not authenticated'}

    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422

    body = {"name": "my_generator", "conditioned": True, "data_format": "image", "task": "classification", "num_classes": None, "model_size": "medium", "epochs": 100, "batch_size": 64, "description": "An awesome classifier"}
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 200
    resp_json = response.json()
    del resp_json["created"]
    assert resp_json == {'batch_size': 64, 'conditioned': True, 'data_format': 'image', 'description': 'An awesome classifier', 'epochs': 100, 'model_size': 'medium', 'name': 'my_generator', 'num_classes': None, 'owner': 'foobar', 'task': 'classification'}

    corrupted_body = body.copy()
    corrupted_body["name"] = "corrupted_onnx"
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.corrupted})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Invalid ONNX model'}

    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 400
    assert response.json() == {'detail': 'Generator with the same name already exists'}

    corrupted_body = body.copy()
    corrupted_body["name"] = "my generator"
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 422

    corrupted_body = body.copy()
    corrupted_body["conditioned"] = 42
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 422

    corrupted_body = body.copy()
    corrupted_body["data_format"] = "tacos"
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 422

    corrupted_body = body.copy()
    corrupted_body["task"] = "birdwatching"
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 422

    corrupted_body = body.copy()
    corrupted_body["num_classes"] = "a lot"
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 422

    corrupted_body = body.copy()
    corrupted_body["model_size"] = "curvy"
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 422

    corrupted_body = body.copy()
    corrupted_body["epochs"] = -1
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 422

    corrupted_body = body.copy()
    corrupted_body["batch_size"] = -1
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 422

    corrupted_body = body.copy()
    corrupted_body["description"] = ""
    response = client.post("/exchange/upload", headers={"Authorization": f"Bearer {token}"}, data=corrupted_body, files={"onnx_file": onnx_file.well_formatted})
    assert response.status_code == 422
