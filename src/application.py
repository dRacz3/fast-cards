from fastapi import FastAPI

from src.database import database_models
from src.database.database import engine
from src.routers import users, cards


def create_app() -> FastAPI:
    database_models.Base.metadata.create_all(bind=engine)
    app = FastAPI()
    app.include_router(users.router)
    app.include_router(cards.router)
    return app
