from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.exchange.router import router as exchange_router
from src.database import Base, engine

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(auth_router)
app.include_router(exchange_router)
