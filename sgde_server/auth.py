import datetime
import re

from flask import Blueprint, request, jsonify
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from .args import Args
from .db import db, User

auth = Blueprint("auth", __name__, url_prefix="/auth")
jwt = JWTManager()


def username_is_valid(username: str) -> tuple[bool, str]:
    if len(username) < Args.MIN_USERNAME_LENGTH:
        return False, f"Username must be at least {Args.MIN_USERNAME_LENGTH} characters long"
    if len(username) > Args.MAX_USERNAME_LENGTH:
        return False, f"Username must be shorter than {Args.MAX_USERNAME_LENGTH} characters"
    if not re.compile(r'^[a-zA-Z]').match(username):
        return False, "Usernames must start with a letter"
    if not re.compile(r'^[a-zA-Z0-9_]+$').match(username):
        return False, "Usernames must contain letters, numbers, and underscores only"
    return True, ""


def password_is_valid(password: str) -> tuple[bool, str]:
    if len(password) < Args.MIN_PASSWORD_LENGTH:
        return False, f"Password must be at least {Args.MIN_PASSWORD_LENGTH} characters long"
    if len(password) > Args.MAX_PASSWORD_LENGTH:
        return False, f"Password must be shorter than {Args.MAX_PASSWORD_LENGTH} characters"
    if not bool(re.search("[a-z]", password)):
        return False, "Password must contain at least one lowercase character"
    if not bool(re.search("[A-Z]", password)):
        return False, "Password must contain at least one uppercase character"
    if not bool(re.search("[0-9]", password)):
        return False, "Password must contain at least one number"
    if not bool(re.search("[!@#$%^&*()]", password)):
        return False, "Password must contain at least one symbol"
    return True, ""


@auth.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username:
        return jsonify(msg="Username is required"), 400

    if not password:
        return jsonify(msg="Password is required"), 400

    valid, msg = username_is_valid(username)
    if not valid:
        return jsonify(msg=msg), 400

    valid, msg = password_is_valid(password)
    if not valid:
        return jsonify(msg=msg), 400

    if User.query.filter_by(username=username).first():
        return jsonify(msg="Username already exists"), 400

    # noinspection PyArgumentList
    user = User(username=username, password=generate_password_hash(password))

    db.session.add(user)
    db.session.commit()
    return jsonify(msg="User created successfully"), 201


@auth.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if not username:
        return jsonify(msg="Username is required"), 400

    if not password:
        return jsonify(msg="Password is required"), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify(msg="User does not exist"), 400

    if not check_password_hash(user.password, password):
        return jsonify(msg="Incorrect password"), 400

    valid_from = datetime.datetime.utcnow()
    valid_until = valid_from + datetime.timedelta(seconds=Args.TOKEN_EXPIRATION_SECONDS)
    access_token = create_access_token(
        identity=username,
        expires_delta=datetime.timedelta(seconds=Args.TOKEN_EXPIRATION_SECONDS)
    )

    return jsonify(
        msg="Login successful",
        access_token=access_token,
        valid_from=valid_from,
        valid_until=valid_until,
    ), 201


@auth.route("/whoami", methods=["GET"])
@jwt_required()
def whoami():
    identity = get_jwt_identity()
    return jsonify(msg=f"You are logged in as {identity}", username=identity), 200
