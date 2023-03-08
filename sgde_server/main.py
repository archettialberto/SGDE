import os

from fastapi import FastAPI

from sgde_server.auth.router import router as auth_router
from sgde_server.config import settings
from sgde_server.exchange.router import router as exchange_router
from sgde_server.database import Base, engine

os.makedirs(settings.INSTANCE_PATH, exist_ok=True)
os.makedirs(settings.GENERATOR_PATH, exist_ok=True)
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(auth_router)
app.include_router(exchange_router)
