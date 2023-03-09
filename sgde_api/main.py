import os

import uvicorn
from fastapi import FastAPI

from sgde_api.auth.router import router as auth_router
from sgde_api.config import settings
from sgde_api.exchange.router import router as exchange_router
from sgde_api.database import Base, engine

os.makedirs(settings.INSTANCE_PATH, exist_ok=True)
os.makedirs(settings.GENERATOR_PATH, exist_ok=True)
Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(auth_router)
app.include_router(exchange_router)


if __name__ == "__main__":
    uvicorn.run(app)
