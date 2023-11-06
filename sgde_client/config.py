import logging

from pydantic import BaseSettings


class Config(BaseSettings):
    API_IP: str = "127.0.0.1"
    API_PORT: int = 8000
    DEBUG_MODE: bool = False

    class Config:
        env_file = ".client.env"


settings = Config()
logger = logging.getLogger("sgde_logger")
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(
    logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
)
logger.addHandler(console_handler)
