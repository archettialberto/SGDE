import os
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    sgde_instance_path: str = os.path.join(os.getcwd(), "instance")
    sgde_generator_path: str = os.path.join(sgde_instance_path, "generators")

    sgde_db_filename: str = "sgde_db.db"
    sgde_sqlalchemy_database_url: str = f"sqlite:///{os.path.join(sgde_instance_path, sgde_db_filename)}"

    sgde_secret_key: str
    sgde_jwt_algorithm: str = "HS256"
    sgde_access_token_expire_minutes: int = 32

    sgde_max_items_from_get: int = 100

    sgde_username_min_len: int = 4
    sgde_username_max_len: int = 16
    sgde_username_regex: str = r"^[a-zA-Z][a-zA-Z0-9_-]*$"
    sgde_username_params: dict = {
        "min_length": sgde_username_min_len,
        "max_length": sgde_username_max_len,
        "regex": sgde_username_regex
    }

    sgde_password_min_len: int = 8
    sgde_password_max_len: int = 32
    sgde_password_regex: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*\W)[a-zA-Z\d\W]+$"
    sgde_password_params: dict = {
        "min_length": sgde_password_min_len,
        "max_length": sgde_password_max_len,
        "regex": sgde_password_regex
    }

    sgde_generator_name_min_len: int = 4
    sgde_generator_name_max_len: int = 32
    sgde_generator_name_regex: str = r"^[a-zA-Z][a-zA-Z0-9_-]*$"
    sgde_generator_name_params: dict = {
        "min_length": sgde_generator_name_min_len,
        "max_length": sgde_generator_name_max_len,
        "regex": sgde_generator_name_regex
    }

    sgde_generator_description_min_len: int = 4
    sgde_generator_description_max_len: int = 1024
    sgde_generator_description_params: dict = {
        "min_length": sgde_generator_description_min_len,
        "max_length": sgde_generator_description_max_len
    }

    class Config:
        env_file = ".env"


# def get_settings() -> Settings:
#     return Settings()
