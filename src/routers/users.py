from typing import List

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

import src.users.crud
import src.users.models
from src.auth.auth_bearer import JWTBearer
from src.auth.auth_handler import signJWT, decodeJWT
from src.auth.models import (
    UserSchema,
    UserLoginSchema,
    TokenResponse,
    LoginFailureMessage,
    LoginCheckResponse,
)
from src.auth.password_hash import verify_password

from src.dependencies import get_db, get_token_header

router = APIRouter(
    prefix="/auth",
    dependencies=[Depends(get_db)],
    tags=["auth"],
)


def check_user(data: UserLoginSchema, db: Session):
    users = src.users.crud.get_users(db)
    for user in users:
        if user.username == data.username and verify_password(
            data.password, user.password
        ):
            return True
    return False


@router.post("/signup", tags=["user"], response_model=TokenResponse)
async def create_user(user: UserSchema = Body(...), db: Session = Depends(get_db)):
    src.users.crud.create_user(db=db, user=user)
    return signJWT(user.username)


@router.post(
    "/login",
    tags=["user"],
    response_model=TokenResponse,
    responses={"403": {"model": LoginFailureMessage}},
)
async def user_login(user: UserLoginSchema = Body(...), db: Session = Depends(get_db)):
    if check_user(user, db):
        return signJWT(user.username)
    return JSONResponse(status_code=403, content=dict(detail="Wrong login details!"))


@router.get(
    "/",
    response_model=List[UserSchema],
    dependencies=[Depends(get_token_header)],
)
def read_users(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
) -> List[UserSchema]:
    users = src.users.crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=src.users.models.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = src.users.crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.get("/is_my_login_valid", response_model=LoginCheckResponse)
def is_my_login_valid(token: str = Depends(JWTBearer())):
    user = decodeJWT(token)
    if user is None:
        raise HTTPException(404, "User not found with this token.")
    return LoginCheckResponse(success=True)
