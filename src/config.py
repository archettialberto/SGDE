import os
from enum import Enum

from pydantic import BaseSettings


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

    @property
    def is_development(self):
        return self == self.DEVELOPMENT

    @property
    def is_testing(self):
        return self == self.TESTING

    @property
    def is_production(self):
        return self == self.PRODUCTION


class Config(BaseSettings):
    DATABASE_URL: str = "sqlite:///./sgde_db.db"

    JWT_ALG: str = "HS256"
    JWT_SECRET: str = "SECRET"
    JWT_EXP: int = "21000"

    ENVIRONMENT: Environment = Environment.DEVELOPMENT

    GENERATOR_PATH: str = os.getcwd()


settings = Config()
