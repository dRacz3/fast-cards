from typing import List

from sqlalchemy.orm import Session

import src.database.database_models
import src.users.models
from src.auth.models import UserSchema
from src.auth.password_hash import hash_password
from src.exceptions import UserNotFoundException


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
    if u is not None:
        return UserSchema(
            username=u.username, email=u.email, password=u.hashed_password
        )
    else:
        raise UserNotFoundException(f"Could not find user with email: {email}")


def get_user_by_username(db: Session, username: str) -> UserSchema:
    u = (
        db.query(src.database.database_models.User)
        .filter(src.database.database_models.User.username == username)
        .first()
    )
    if u is not None:
        return UserSchema(
            username=u.username, email=u.email, password=u.hashed_password
        )
    else:
        raise UserNotFoundException(f"Could not find user with username: {username}")


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserSchema]:
    users_in_db: List[src.database.database_models.User] = (
        db.query(src.database.database_models.User).offset(skip).limit(limit).all()
    )
    return [
        UserSchema(username=u.username, email=u.email, password=u.hashed_password)
        for u in users_in_db
    ]


def create_user(db: Session, user: UserSchema):
    hashed_password = str(hash_password(user.password))
    db_user = src.database.database_models.User(
        email=user.email, hashed_password=hashed_password, username=user.username
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
