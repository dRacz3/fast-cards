from typing import List

from sqlalchemy.orm import Session

import src.database.database_models
import src.users.models
from src.auth.models import UserSchema


def get_user(db: Session, user_id: int):
    return (
        db.query(src.database.database_models.User)
        .filter(src.database.database_models.User.id == user_id)
        .first()
    )


def get_user_by_email(db: Session, email: str) -> UserSchema:
    u = (
        db.query(src.database.database_models.User)
        .filter(src.database.database_models.User.email == email)
        .first()
    )
    return UserSchema(username=u.username, email=u.email, password=u.hashed_password)


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserSchema]:
    users_in_db: List[src.database.database_models.User] = (
        db.query(src.database.database_models.User).offset(skip).limit(limit).all()
    )
    return [
        UserSchema(username=u.username, email=u.email, password=u.hashed_password)
        for u in users_in_db
    ]


def create_user(db: Session, user: UserSchema):
    fake_hashed_password = user.password
    db_user = src.database.database_models.User(
        email=user.email, hashed_password=fake_hashed_password, username=user.username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
