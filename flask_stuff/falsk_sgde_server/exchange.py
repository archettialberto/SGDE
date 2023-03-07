import os
import uuid
from pathlib import Path

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from falsk_sgde_server.utils import get_field_from_request, safe_exception_raise, check_str_len, check_task_name_is_new, \
    get_task, check_generator_name_is_new, query_to_dict, get_generator
from falsk_sgde_server.db import db, User, Task, Generator

exchange = Blueprint("exchange", __name__, url_prefix="/exchange")


@exchange.route("/tasks", methods=["GET"])
@jwt_required()
@safe_exception_raise
def get_tasks():
    tasks = Task.query.join(User, User.id == Task.user_id).with_entities(Task.name, User.username)
    return jsonify(
        msg="Tasks retrieved successfully",
        tasks=query_to_dict(tasks, ["task_name", "creator"])
    ), 200


@exchange.route("/tasks", methods=["POST"])
@jwt_required()
@safe_exception_raise
def post_task():
    task_name = get_field_from_request(request, "task_name")
    min_len, max_len = current_app.config["MIN_TASK_NAME_LENGTH"], current_app.config["MAX_TASK_NAME_LENGTH"]
    check_str_len(task_name, "task_name", min_len, max_len)

    check_task_name_is_new(task_name)

    user = User.query.filter_by(username=get_jwt_identity()).first()
    task_dir = str(uuid.uuid4())
    os.makedirs(Path(current_app.instance_path, "tasks", task_dir), exist_ok=True)

    # noinspection PyArgumentList
    task = Task(name=task_name, directory=task_dir, user_id=user.id)
    db.session.add(task)
    db.session.commit()
    return jsonify(msg="Task created successfully"), 201


@exchange.route("/generators", methods=["GET"])
@jwt_required()
@safe_exception_raise
def get_generators():
    task_name = get_field_from_request(request, "task_name")
    min_len, max_len = current_app.config["MIN_TASK_NAME_LENGTH"], current_app.config["MAX_TASK_NAME_LENGTH"]
    check_str_len(task_name, "task_name", min_len, max_len)

    task = get_task(task_name)

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
@safe_exception_raise
def upload_generator():
    task_name = get_field_from_request(request, "task_name")
    min_len, max_len = current_app.config["MIN_TASK_NAME_LENGTH"], current_app.config["MAX_TASK_NAME_LENGTH"]
    check_str_len(task_name, "task_name", min_len, max_len)

    generator_name = get_field_from_request(request, "generator_name")
    min_len, max_len = current_app.config["MIN_GENERATOR_NAME_LENGTH"], current_app.config["MAX_GENERATOR_NAME_LENGTH"]
    check_str_len(generator_name, "generator_name", min_len, max_len)

    onnx_data = get_field_from_request(request, "onnx")

    task = get_task(task_name)
    check_generator_name_is_new(generator_name, task.id)

    user = User.query.filter_by(username=get_jwt_identity()).first()

    filename = str(uuid.uuid4())
    with open(Path(current_app.instance_path, "tasks", task.directory, f"{filename}.onnx"), 'w') as f:
        f.write(onnx_data)
    # noinspection PyArgumentList
    generator = Generator(name=generator_name, filename=filename, task_id=task.id, user_id=user.id)
    db.session.add(generator)
    db.session.commit()
    return jsonify(msg="Generator uploaded successfully"), 201


@exchange.route("/generators/download", methods=["GET"])
@jwt_required()
@safe_exception_raise
def download_generator():
    task_name = get_field_from_request(request, "task_name")
    min_len, max_len = current_app.config["MIN_TASK_NAME_LENGTH"], current_app.config["MAX_TASK_NAME_LENGTH"]
    check_str_len(task_name, "task_name", min_len, max_len)

    generator_name = get_field_from_request(request, "generator_name")
    min_len, max_len = current_app.config["MIN_GENERATOR_NAME_LENGTH"], current_app.config["MAX_GENERATOR_NAME_LENGTH"]
    check_str_len(generator_name, "generator_name", min_len, max_len)

    task = get_task(task_name)
    generator = get_generator(generator_name, task.id)

    file_path = Path(current_app.instance_path, "tasks", task.directory, f"{generator.filename}.onnx")
    with open(file_path, 'r') as f:
        onnx_data = f.read()
    return jsonify(msg="Generator downloaded successfully", onnx=onnx_data), 200
