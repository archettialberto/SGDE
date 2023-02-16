import datetime

from flask import Blueprint, request, jsonify, current_app
from flask_bcrypt import generate_password_hash
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from sgde_server.utils import get_field_from_request, check_valid_username, safe_exception_raise, \
    check_valid_password, check_username_is_new, get_user, check_correct_password
from sgde_server.db import db, User

auth = Blueprint("auth", __name__, url_prefix="/auth")
jwt = JWTManager()


@auth.route("/register", methods=["POST"])
@safe_exception_raise
def register():
    username = get_field_from_request(request, "username")
    check_valid_username(username, current_app.config["MIN_USERNAME_LENGTH"], current_app.config["MAX_USERNAME_LENGTH"])

    password = get_field_from_request(request, "password")
    check_valid_password(password, current_app.config["MIN_PASSWORD_LENGTH"], current_app.config["MAX_PASSWORD_LENGTH"])

    check_username_is_new(username)

    # noinspection PyArgumentList
    user = User(username=username, password=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify(msg="User created successfully"), 201


@auth.route("/login", methods=["POST"])
@safe_exception_raise
def login():
    username = get_field_from_request(request, "username")
    check_valid_username(username, current_app.config["MIN_USERNAME_LENGTH"], current_app.config["MAX_USERNAME_LENGTH"])

    password = get_field_from_request(request, "password")
    check_valid_password(password, current_app.config["MIN_PASSWORD_LENGTH"], current_app.config["MAX_PASSWORD_LENGTH"])

    user = get_user(username)

    check_correct_password(user.password, password)

    valid_for_sec = current_app.config["TOKEN_EXPIRATION_SECONDS"]
    valid_until = datetime.datetime.utcnow() + datetime.timedelta(seconds=valid_for_sec)
    access_token = create_access_token(identity=username, expires_delta=datetime.timedelta(seconds=valid_for_sec))

    return jsonify(msg="Login successful", access_token=access_token, valid_until=valid_until), 201


@auth.route("/whoami", methods=["GET"])
@jwt_required()
@safe_exception_raise
def whoami():
    identity = get_jwt_identity()
    return jsonify(msg=f"You are logged in as '{identity}'", username=identity), 200
