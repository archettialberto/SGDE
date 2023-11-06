import json
import os
import shutil

import pytest
from fastapi import FastAPI
from onnx import TensorProto
from onnx.checker import check_model
from onnx.helper import make_tensor_value_info, make_node, make_model, make_graph
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.testclient import TestClient

from sgde_api.auth.router import router as auth_router
from sgde_api.config import settings
from sgde_api.database import Base, get_db
from sgde_api.exchange.router import router as exchange_router

settings.INSTANCE_PATH = os.path.join(os.getcwd(), "test_instance")
settings.DATABASE_URL = os.path.join(os.getcwd(), "test_instance", "sgde_test_db.db")
settings.GENERATOR_PATH = os.path.join(os.getcwd(), "test_instance", "generators")
os.makedirs(settings.INSTANCE_PATH, exist_ok=True)
os.makedirs(settings.GENERATOR_PATH, exist_ok=True)
engine = create_engine(
    f'sqlite:///{os.path.join(settings.INSTANCE_PATH, "sgde_test_db.db")}',
    connect_args={"check_same_thread": False},
)
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)

foobar = {"username": "foobar", "email": "foobar@example.com", "password": "aaaAAA1!"}

foo_gan = {
    "name": "foo_gan",
    "data_name": "mnist",
    "data_description": "MNIST dataset",
    "data_structure": "image",
    "data_length": 60000,
    "task": "classification",
    "metric": "accuracy",
    "best_score": 0.97,
    "best_score_real": 0.98,
}


def start_application() -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(exchange_router)
    return app


@pytest.fixture(scope="function")
def app():
    os.makedirs(settings.INSTANCE_PATH, exist_ok=True)
    os.makedirs(settings.GENERATOR_PATH, exist_ok=True)
    Base.metadata.create_all(engine)
    _app = start_application()
    yield _app
    Base.metadata.drop_all(engine)
    for item in os.listdir(settings.GENERATOR_PATH):
        if item.endswith(".onnx"):
            os.remove(os.path.join(settings.GENERATOR_PATH, item))


@pytest.fixture(scope="function")
def db_session(app):
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionTesting(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="session", autouse=True)
def cleanup_db(request):
    def remove_test_dir():
        shutil.rmtree(settings.INSTANCE_PATH)

    request.addfinalizer(remove_test_dir)


@pytest.fixture(scope="function")
def client(app, db_session):
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as fixture_client:
        yield fixture_client


@pytest.fixture(scope="module")
def onnx_file():
    onnx_folder = os.path.join(os.getcwd(), "test_onnx")
    os.makedirs(onnx_folder, exist_ok=True)

    _X = make_tensor_value_info("X", TensorProto.FLOAT, [None, None])
    _A = make_tensor_value_info("A", TensorProto.FLOAT, [None, None])
    _B = make_tensor_value_info("B", TensorProto.FLOAT, [None, None])
    _Y = make_tensor_value_info("Y", TensorProto.FLOAT, [None])
    node1 = make_node("MatMul", ["X", "A"], ["XA"])
    node2 = make_node("Add", ["XA", "B"], ["Y"])
    graph = make_graph([node1, node2], "lr", [_X, _A, _B], [_Y])
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


@pytest.fixture(scope="module")
def json_file():
    json_folder = os.path.join(os.getcwd(), "test_json")
    os.makedirs(json_folder, exist_ok=True)

    with open(os.path.join(json_folder, "json_model.json"), "w") as f:
        json.dump(foo_gan, f)

    with open(os.path.join(json_folder, "wrong_json_model.json"), "w") as f:
        json.dump({"list_of_list": [[]]}, f)

    class JSONFileBearer:
        def __init__(self):
            with open(os.path.join(json_folder, "json_model.json"), "r") as f:
                self.well_formatted = f.read()

            with open(os.path.join(json_folder, "wrong_json_model.json"), "r") as f:
                self.corrupted = f.read()

    yield JSONFileBearer()
    shutil.rmtree(json_folder)


def register_and_login(fixture_client):
    fixture_client.post("/auth/register", json=foobar)
    response = fixture_client.post(
        "/auth/token",
        data={"username": foobar["username"], "password": foobar["password"]},
    )
    token = response.json()["access_token"]
    return token
