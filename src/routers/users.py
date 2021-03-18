from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

import cards_server.users.crud
import cards_server.users.models

from cards_server.dependencies import get_db, get_token_header

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(get_db)],
    tags=["users"],
)


@router.post("/", response_model=cards_server.users.models.User)
def create_user(user: cards_server.users.models.UserCreate, db: Session = Depends(get_db)):
    db_user = cards_server.users.crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return cards_server.users.crud.create_user(db=db, user=user)


@router.get(
    "/",
    response_model=List[cards_server.users.models.User],
    dependencies=[Depends(get_token_header)],
)
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = cards_server.users.crud.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=cards_server.users.models.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = cards_server.users.crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
