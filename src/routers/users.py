from typing import List

from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session

import src.users.crud
import src.users.models
from src.auth.auth_handler import signJWT
from src.auth.models import UserSchema, UserLoginSchema

from src.dependencies import get_db, get_token_header

router = APIRouter(
    prefix="/auth",
    dependencies=[Depends(get_db)],
    tags=["auth"],
)

# Replace with db
users = []


def check_user(data: UserLoginSchema):
    for user in users:
        if user.email == data.email and user.password == data.password:
            return True
    return False

@router.post("/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    users.append(user)  # replace with db call, making sure to hash the password first
    return signJWT(user.email)


@router.post("/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    if check_user(user):
        return signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }


@router.post("/", response_model=src.users.models.User)
def create_user(user: src.users.models.UserCreate, db: Session = Depends(get_db)):
    db_user = src.users.crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return src.users.crud.create_user(db=db, user=user)


@router.get(
    "/",
    response_model=List[src.users.models.User],
    dependencies=[Depends(get_token_header)],
)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = src.users.crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=src.users.models.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = src.users.crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
