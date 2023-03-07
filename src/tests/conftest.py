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

from src.auth.router import router as auth_router
from src.database import Base, get_db
from src.exchange.router import router as exchange_router

engine = create_engine(
    f"sqlite:///{os.path.join(os.getcwd(), 'test_instance_dir', 'sgde_test_db.db')}",
    connect_args={"check_same_thread": False}
)
SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def start_application() -> FastAPI:
    app = FastAPI()
    app.include_router(auth_router)
    app.include_router(exchange_router)
    return app


@pytest.fixture(scope="function")
def app():
    os.makedirs(os.path.join(os.getcwd(), "test_instance_dir"), exist_ok=True)
    Base.metadata.create_all(engine)
    _app = start_application()
    yield _app
    Base.metadata.drop_all(engine)
    for item in os.listdir(os.getcwd()):
        # TODO fix paths for onnx models
        if item.endswith(".onnx"):
            os.remove(os.path.join(os.getcwd(), item))


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
        shutil.rmtree(os.path.join(os.getcwd(), "test_instance_dir"))
    request.addfinalizer(remove_test_dir)


@pytest.fixture(scope="function")
def client(app, db_session):

    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client


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
