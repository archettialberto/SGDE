import re

from flask import jsonify, Request
from flask_bcrypt import check_password_hash
from flask_sqlalchemy.query import Query

from .db import User, Task, Generator


def query_to_dict(query: Query, columns: list[str]) -> dict[str, list]:
    res = {}
    for i, c in enumerate(columns):
        res[c] = [r[i] for r in list(query)]
    return res


class APIException(Exception):
    def __init__(self, error_number: int, message: str):
        self.message = message
        self.error_number = error_number
        super().__init__(self.message)


def safe_exception_raise(fn):
    def wrapper_fn(*args, **kwargs):
        try:
            message, code = fn(*args, **kwargs)
            return message, code
        except APIException as e:
            return jsonify(msg=e.message), e.error_number

    wrapper_fn.__name__ = fn.__name__
    return wrapper_fn


def get_field_from_request(request: Request, field: str, required=True):
    username = request.form.get(field)
    if required:
        if username is None:
            raise APIException(400, f"Field '{field}' is required")
    return username


def check_str_len(s: str, field: str, min_len: int, max_len: int):
    if len(s) < min_len:
        raise APIException(400, f"'{field}' must be at least {min_len} characters long")
    if len(s) > max_len:
        raise APIException(400, f"'{field}' must be at most {max_len} characters long")


def check_valid_username(username: str, min_len: int, max_len: int):
    check_str_len(username, "username", min_len, max_len)
    if not re.compile(r'^[a-zA-Z]').match(username):
        raise APIException(400, "'username' must start with a letter")
    if not re.compile(r'^[a-zA-Z0-9_]+$').match(username):
        raise APIException(400, "'username' must contain letters, numbers, and underscores only")


def check_valid_password(password: str, min_len: int, max_len: int):
    check_str_len(password, "password", min_len, max_len)
    if not bool(re.search("[a-z]", password)):
        raise APIException(400, "'password' must contain at least one lowercase character")
    if not bool(re.search("[A-Z]", password)):
        raise APIException(400, "'password' must contain at least one uppercase character")
    if not bool(re.search("[0-9]", password)):
        raise APIException(400, "'password' must contain at least one number")
    if not bool(re.search("[!@#$%^&*()]", password)):
        raise APIException(400, "'password' must contain at least one symbol")
    if not re.compile(r'^[a-zA-Z0-9!@#$%^&*()]+$').match(password):
        raise APIException(400, "'password' must contain letters, numbers, and symbols only")


def check_correct_password(true_password: str, password: str):
    if not check_password_hash(true_password, password):
        raise APIException(400, "Incorrect password")


def get_user(username: str, exists=True):
    user = User.query.filter_by(username=username).first()
    if exists and not user:
        raise APIException(400, "'username' does not exist")
    return user


def get_task(task_name: str, exists=True):
    task = Task.query.filter_by(name=task_name).first()
    if exists and not task:
        raise APIException(400, "'task_name' does not exist")
    return task


def get_generator(generator_name: str, task_id: int, exists=True):
    generator = Generator.query.filter_by(name=generator_name, task_id=task_id).first()
    if exists and not generator:
        raise APIException(400, f"'generator_name' does not exist for 'task_name'")
    return generator


def check_username_is_new(username: str):
    if get_user(username, exists=False):
        raise APIException(400, "'username' already exists")


def check_task_name_is_new(task_name: str):
    if get_task(task_name, exists=False):
        raise APIException(400, "'task_name' already exists")


def check_generator_name_is_new(generator_name: str, task_id: int):
    if get_generator(generator_name, task_id, exists=False):
        raise APIException(400, "'generator_name' already exists for task 'task_name'")
