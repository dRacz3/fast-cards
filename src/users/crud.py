from sqlalchemy.orm import Session

import src.users.sql_models
import src.users.models


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


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(src.users.sql_models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: src.users.models.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = src.users.sql_models.User(
        email=user.email, hashed_password=fake_hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
