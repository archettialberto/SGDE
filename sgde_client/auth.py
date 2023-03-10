import os
from getpass import getpass

import pandas as pd

from utils import post_request, get_request


@post_request()
def register_request():
    username = str(input("Insert username: "))
    email = str(input("Insert email: "))
    password = str(getpass("Insert password: "))
    confirmed_password = str(getpass("Confirm password: "))
    if password != confirmed_password:
        raise ValueError("Passwords must match")
    return "auth/register", {"json": {"username": username, "email": email, "password": password}}


def register():
    response = register_request()
    print(f"Registered as {response.json()['username']} ({response.json()['email']})")


@post_request()
def token_request():
    username = str(input("Insert username: "))
    password = str(getpass("Insert password: "))
    return "auth/token", {"data": {"username": username, "password": password}}


def login():
    response = token_request()
    os.environ["ACCESS_TOKEN"] = response.json()["access_token"]
    print(f"Successfully logged in")


@get_request(authenticate=True)
def whoami_request():
    return "auth/whoami", {}


def whoami():
    response = whoami_request()
    user = response.json()
    print(f"Logged in as {user['username']} ({user['email']})")


@get_request()
def get_users_request(skip: int = 0, limit: int = 10):
    return f"users?skip={skip}&limit={limit}", {}


def get_users(skip: int = 0, limit: int = 10):
    response = get_users_request(skip=skip, limit=limit)
    return pd.DataFrame(response.json())


@get_request()
def get_user_request(username: str):
    return f"users/{username}", {}


def get_user(username: str):
    response = get_user_request(username=username)
    return pd.DataFrame([response.json()])
