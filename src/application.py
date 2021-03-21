from fastapi import FastAPI

from src.database import database_models
from src.database.database import engine
from src.routers import users, cards
from src.config import get_settings


def create_app() -> FastAPI:
    print(f"Creating app with settings: {get_settings()}")
    database_models.Base.metadata.create_all(bind=engine)
    app = FastAPI(title="fast-cards", version="0.0.1")
    app.include_router(users.router)
    app.include_router(cards.router)
    return app
