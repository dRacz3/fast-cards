from typing import List

from sqlalchemy.orm import Session

import src.users.sql_models
import src.users.models
from src.auth.models import UserSchema


def get_user(db: Session, user_id: int):
    return (
        db.query(src.users.sql_models.User)
        .filter(src.users.sql_models.User.id == user_id)
        .first()
    )


def get_user_by_email(db: Session, email: str):
    return (
        db.query(src.users.sql_models.User)
        .filter(src.users.sql_models.User.email == email)
        .first()
    )


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserSchema]:
    users_in_db : List[src.users.sql_models.User] = db.query(src.users.sql_models.User).offset(skip).limit(limit).all()
    return [UserSchema(username = u.username,
                       email=u.email,
                       password=u.hashed_password) for u in users_in_db]


def create_user(db: Session, user: src.users.models.UserCreate):
    fake_hashed_password = user.password
    db_user = src.users.sql_models.User(
        email=user.email, hashed_password=fake_hashed_password,
        username = user.username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_2(db: Session, user: UserSchema):
    fake_hashed_password = user.password
    db_user = src.users.sql_models.User(
        email=user.email,
        hashed_password=fake_hashed_password,
        username = user.username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
