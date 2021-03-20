from src.auth.auth_handler import decodeJWT
from src.database.database import SessionLocal
from src.users.crud import get_user_by_email


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from fastapi import Header, HTTPException, Depends


async def get_token_header(x_token: str = Header(...), db=Depends(get_db)):
    token = decodeJWT(x_token)
    if token is None:
        raise HTTPException(status_code=400, detail="X-Token header invalid")
    user = get_user_by_email(db, token.user_id)
    if user is None:
        raise HTTPException(
            status_code=404, detail="No user is associated with the token"
        )
