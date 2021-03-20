import sqlite3

import pytest
from sqlalchemy.orm import Session

from src.database.database import engine
from src.database.database_models import User
from src.users.crud import create_user, get_users
from src.users.models import UserCreate


@pytest.fixture(autouse=True)
def drop_users(database_connection):
    db = database_connection
    try:
        num_rows_deleted = db.query(User).delete()
        db.commit()
    except:
        db.rollback()


def test_get_user(database_connection):
    db = database_connection
    created_user = create_user(db, UserCreate(email="asd@hello.com",
                           username="mr.asd",
                           password="nyeh"))

    users_in_db = get_users(db)
    assert len(users_in_db) == 1
    for u in users_in_db:
        assert u.email == created_user.email
        assert u.username == created_user.username
        assert u.password == created_user.hashed_password
