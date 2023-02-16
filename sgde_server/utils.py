import re

from flask import jsonify, Request
from flask_bcrypt import check_password_hash
from flask_sqlalchemy.query import Query

from sgde_server.exceptions import APIException, MissingFieldException, InvalidFormatException, \
    IncorrectPasswordException, DoesNotExistException, AlreadyExistsException
from sgde_server.db import User, Task, Generator


def query_to_dict(query: Query, columns: list[str]) -> dict[str, list]:
    res = {}
    for i, c in enumerate(columns):
        res[c] = [r[i] for r in list(query)]
    return res


def safe_exception_raise(fn):
    def wrapper_fn(*args, **kwargs):
        try:
            message, code = fn(*args, **kwargs)
            return message, code
        except APIException as e:
            return jsonify(msg=e.msg), e.status_code

    wrapper_fn.__name__ = fn.__name__
    return wrapper_fn


# TODO type check?
def get_field_from_request(request: Request, field_name: str, required=True):
    username = request.form.get(field_name)
    if required:
        if username is None:
            raise MissingFieldException(field_name)
    return username


def check_str_len(s: str, field_name: str, min_len: int, max_len: int):
    if len(s) < min_len:
        raise InvalidFormatException(field_name, InvalidFormatException.TOO_SHORT)
    if len(s) > max_len:
        raise InvalidFormatException(field_name, InvalidFormatException.TOO_LONG)


def check_valid_username(username: str, min_len: int, max_len: int):
    check_str_len(username, "username", min_len, max_len)
    if not re.compile(r"^[a-zA-Z]").match(username):
        raise InvalidFormatException("username", InvalidFormatException.MUST_START_WITH_CHAR)
    if not re.compile(r"^[a-zA-Z0-9_]+$").match(username):
        raise InvalidFormatException("username", InvalidFormatException.USR_CHARS)


def check_valid_password(password: str, min_len: int, max_len: int):
    check_str_len(password, "password", min_len, max_len)
    if not bool(re.search("[a-z]", password)):
        raise InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_L_CHAR)
    if not bool(re.search("[A-Z]", password)):
        raise InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_U_CHAR)
    if not bool(re.search("[0-9]", password)):
        raise InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_NUMBER)
    if not bool(re.search("[!@#$%^&*()]", password)):
        raise InvalidFormatException("password", InvalidFormatException.PWD_CONTAIN_SYMBOL)


def check_correct_password(true_password: str, password: str):
    if not check_password_hash(true_password, password):
        raise IncorrectPasswordException()


def get_user(username: str, exists=True):
    user = User.query.filter_by(username=username).first()
    if exists and not user:
        raise DoesNotExistException("username")
    return user


def get_task(task_name: str, exists=True):
    task = Task.query.filter_by(name=task_name).first()
    if exists and not task:
        raise DoesNotExistException("task_name")
    return task


def get_generator(generator_name: str, task_id: int, exists=True):
    generator = Generator.query.filter_by(name=generator_name, task_id=task_id).first()
    if exists and not generator:
        raise DoesNotExistException("task_name'+'generator_name")
    return generator


def check_username_is_new(username: str):
    if get_user(username, exists=False):
        raise AlreadyExistsException("username")


def check_task_name_is_new(task_name: str):
    if get_task(task_name, exists=False):
        raise AlreadyExistsException("task_name")


def check_generator_name_is_new(generator_name: str, task_id: int):
    if get_generator(generator_name, task_id, exists=False):
        raise AlreadyExistsException("task_name'+'generator_name")
