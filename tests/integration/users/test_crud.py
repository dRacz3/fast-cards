import pytest
from pydantic import EmailStr

from src.auth.models import UserSchema
from src.database.database_models import User
from src.users.crud import get_users, get_user_by_email, create_user


@pytest.fixture()
def insert_default_user(database_connection):
    db = database_connection
    created_user = create_user(
        db,
        UserSchema(email=EmailStr("asd@hello.com"), username="mr.asd", password="nyeh"),
    )
    yield created_user


def test_get_user(database_connection):
    db = database_connection
    created_user = create_user(
        db,
        UserSchema(email=EmailStr("asd@hello.com"), username="mr.asd", password="nyeh"),
    )

    users_in_db = get_users(db)
    assert len(users_in_db) == 1
    for u in users_in_db:
        assert u.email == created_user.email
        assert u.username == created_user.username
        assert u.password == created_user.hashed_password


def test_get_user_by_email(insert_default_user, database_connection):
    db = database_connection
    user = insert_default_user
    returend_user = get_user_by_email(db, user.email)
    assert returend_user.email == user.email
    assert returend_user.username == user.username
