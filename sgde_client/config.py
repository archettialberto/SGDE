from pydantic import BaseSettings


class Config(BaseSettings):
    API_IP: str = "127.0.0.1"
    API_PORT: int = 8000

    class Config:
        env_file = ".client.env"


settings = Config()
