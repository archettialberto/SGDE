import os
import uuid
from pathlib import Path

from flask_sqlalchemy.query import Query
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from .args import Args
from .db import db, User, Task, Generator

exchange = Blueprint("exchange", __name__, url_prefix="/exchange")


def query_to_dict(query: Query, columns: list[str]) -> dict[str, list]:
    res = {}
    for i, c in enumerate(columns):
        res[c] = [r[i] for r in list(query)]
    return res


@exchange.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    tasks = Task.query.join(User, User.id == Task.user_id).with_entities(Task.name, User.username)
    return jsonify(
        msg="Tasks retrieved successfully",
        tasks=query_to_dict(tasks, ["task_name", "creator"])
    ), 200


@exchange.route("/tasks", methods=["POST"])
@jwt_required()
def post_task():
    task_name = request.form.get("task_name")
    if not task_name:
        return jsonify(msg="Task name is required"), 400

    if len(task_name) < Args.MIN_TASK_NAME_LENGTH:
        return jsonify(msg=f"Task name must be at least {Args.MIN_TASK_NAME_LENGTH} characters long"), 400
    if len(task_name) > Args.MAX_TASK_NAME_LENGTH:
        return jsonify(msg=f"Task name must shorter than {Args.MAX_TASK_NAME_LENGTH} characters"), 400

    if Task.query.filter_by(name=task_name).first():
        return jsonify(msg="Task name already exists"), 400

    user = User.query.filter_by(username=get_jwt_identity()).first()
    task_dir = str(uuid.uuid4())
    os.makedirs(Path("instance", "generators", task_dir), exist_ok=True)

    # noinspection PyArgumentList
    task = Task(name=task_name, directory=task_dir, user_id=user.id)

    db.session.add(task)
    db.session.commit()
    return jsonify(msg="Task created successfully"), 201


@exchange.route("/generators", methods=["GET"])
@jwt_required()
def get_generators():
    task_name = request.form.get("task_name")
    if not task_name:
        return jsonify(msg="Task name is required"), 400

    task = Task.query.filter_by(name=task_name).first()
    if not task:
        return jsonify(msg=f"Task {task_name} does not exist"), 400

    generators = Generator.query. \
        join(User, User.id == Generator.user_id). \
        filter(Generator.task_id == task.id). \
        with_entities(Generator.name, User.username)

    return jsonify(
            msg="Generators retrieved successfully",
            generators=query_to_dict(generators, ["generator_name", "creator"])
        ), 200


@exchange.route("generators/upload", methods=["POST"])
@jwt_required()
def upload_generator():
    task_name = request.form.get("task_name")
    if not task_name:
        return jsonify(msg="Task name is required"), 400

    generator_name = request.form.get("generator_name")
    if not generator_name:
        return jsonify(msg="Generator name is required"), 400

    if len(task_name) < Args.MIN_GENERATOR_NAME_LENGTH:
        return jsonify(msg=f"Generator name must be at least {Args.MIN_GENERATOR_NAME_LENGTH} characters long"), 400
    if len(task_name) > Args.MAX_GENERATOR_NAME_LENGTH:
        return jsonify(msg=f"Generator name must shorter than {Args.MAX_GENERATOR_NAME_LENGTH} characters"), 400

    task = Task.query.filter_by(name=task_name).first()
    if not task:
        return jsonify(msg=f"Task {task_name} does not exist"), 400

    generator_same_name = Generator.query.filter(Generator.task_id == task.id, Generator.name == generator_name).first()
    if generator_same_name:
        return jsonify(msg=f"Generator names {generator_name} already exists"), 400

    user = User.query.filter_by(username=get_jwt_identity()).first()

    onnx = request.form.get("onnx")
    if not onnx:
        return jsonify(msg="ONNX file is required"), 400

    filename = str(uuid.uuid4())

    with open(Path("instance", "generators", task.directory, f"{filename}.onnx"), 'w') as f:
        f.write(onnx)

    # noinspection PyArgumentList
    generator = Generator(name=generator_name, filename=filename, task_id=task.id, user_id=user.id)

    db.session.add(generator)
    db.session.commit()
    return jsonify(msg="Generator uploaded successfully"), 201


@exchange.route("/generators/download", methods=["GET"])
@jwt_required()
def download_generator():
    task_name = request.form.get("task_name")
    if not task_name:
        return jsonify(msg="Task name is required"), 400

    task = Task.query.filter_by(name=task_name).first()
    if not task:
        return jsonify(msg=f"Task {task_name} does not exist"), 400

    generator_name = request.form.get("generator_name")
    if not generator_name:
        return jsonify(msg="Generator name is required"), 400

    generator = Generator.query.filter_by(name=generator_name, task_id=task.id).first()
    if not generator:
        return jsonify(msg=f"Generator named {generator}  for task {task_name} does not exist"), 400

    with open(Path("instance", "generators", task.directory, f"{generator.filename}.onnx"), 'r') as f:
        onnx = f.read()

    return jsonify(
            msg="Generator downloaded successfully",
            onnx=onnx
        ), 200
