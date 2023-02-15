import os
from pathlib import Path

import pytest

from sgde_server.exceptions import MissingFieldException, InvalidFormatException, AlreadyExistsException
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


def check_response(resp, code, msg):
    assert resp.status_code == code and resp.json["msg"] == msg


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
    check_response(resp, 400, MissingFieldException("task_name").msg)

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "t"})
    check_response(resp, 400, InvalidFormatException("task_name", InvalidFormatException.TOO_SHORT).msg)

    long_task_name = 'foo' * app.config['MAX_TASK_NAME_LENGTH']
    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": f"{long_task_name}"})
    check_response(resp, 400, InvalidFormatException("task_name", InvalidFormatException.TOO_LONG).msg)

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task"})
    assert resp.status_code == 201

    resp = client.get("/exchange/tasks", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200 and resp.json["tasks"] == {"creator": ["foo_bar"], "task_name": ["sample_task"]}

    resp = client.post("/exchange/tasks", headers={"Authorization": f"Bearer {token}"},
                       data={"task_name": "sample_task"})
    check_response(resp, 400, AlreadyExistsException("task_name").msg)


def generator_exchange(app, client):
    # TODO implement these tests
    pass
