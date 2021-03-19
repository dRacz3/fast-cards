import uvicorn
from fastapi import Depends, FastAPI


from src.database import crud, sql_models, schema
from src.database.database import engine
from src.dependencies import get_db, get_token_header
from src.routers import items, users, cards

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
    uvicorn.run('main:app', host="0.0.0.0", port=8000, debug=True, reload=True)
