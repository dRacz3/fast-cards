from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import database_models
from src.database.database import engine
from src.routers import users, cards, websocket_endpoints, game
from src.config import get_settings


def create_app() -> FastAPI:
    print(f"Creating app with settings: {get_settings()}")
    database_models.Base.metadata.create_all(bind=engine)
    app = FastAPI(title="fast-cards", version="0.0.1")

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(users.router)
    app.include_router(cards.router)
    app.include_router(websocket_endpoints.router)
    app.include_router(game.router)

    return app
