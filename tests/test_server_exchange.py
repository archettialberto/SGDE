import os
from pathlib import Path

import pytest

from sgde_server.exceptions import MissingFieldException, InvalidFormatException, AlreadyExistsException, APIException
from sgde_server import create_app


@pytest.fixture()
def app():
    app = create_app(instance_path=Path(os.getcwd(), "test_instance"))
    app.config.update({"TESTING": True})
    yield app
    os.system(f"rm -rf {app.instance_path}")


@pytest.fixture()
def client(app):
    return app.test_client()


def check_exception(resp, exception: APIException):
    assert resp.status_code == exception.status_code and resp.json["msg"] == exception.msg


def test_task_exchange(app, client):
    resp = client.post("/auth/register", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201

    resp = client.post("/auth/login", data={"username": "foo_bar", "password": "aaaaAAAA1111!"})
    assert resp.status_code == 201

    token = resp.json["access_token"]
    resp = client.get("/auth/whoami", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

    resp = client.get("/exchange/tasks")
    assert resp.status_code == 401 and "Missing Authorization Header" == resp.json["msg"]

    resp = client.get("/exchange/tasks", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200 and resp.json["tasks"] == {"creator": [], "task_name": []}

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={})
    check_exception(resp, MissingFieldException("task_name"))

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "t"})
    check_exception(resp, InvalidFormatException("task_name", InvalidFormatException.TOO_SHORT))

    long_task_name = 'foo' * app.config['MAX_TASK_NAME_LENGTH']
    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": f"{long_task_name}"})
    check_exception(resp, InvalidFormatException("task_name", InvalidFormatException.TOO_LONG))

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task"})
    assert resp.status_code == 201

    resp = client.get("/exchange/tasks", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200 and resp.json["tasks"] == {"creator": ["foo_bar"], "task_name": ["sample_task"]}

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task"})
    check_exception(resp, AlreadyExistsException("task_name"))


def generator_exchange(app, client):
    # TODO implement these tests
    pass
