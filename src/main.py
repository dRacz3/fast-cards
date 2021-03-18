import uvicorn
from fastapi import Depends, FastAPI


from cards_server.database import crud, sql_models, schema
from cards_server.database.database import engine
from cards_server.dependencies import get_db, get_token_header
from cards_server.routers import items, users, cards

sql_models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(users.router)
app.include_router(items.router)
app.include_router(cards.router)
# app.include_router(
#     admin.router,
#     prefix="/admin",
#     tags=["admin"],
#     dependencies=[Depends(get_token_header)],
#     responses={418: {"description": "I'm a teapot"}},
# )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
