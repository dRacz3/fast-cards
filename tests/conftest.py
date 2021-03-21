from typing import Any

import pytest
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

import src.application
from src.database.database import SessionLocal
from src.database.database_models import User


def drop_table_content(db: Session, table_model: Any):
    try:
        _ = db.query(table_model).delete()
        db.commit()
    except:
        db.rollback()

def default_header() -> dict:
    return {
        "accept": "application/json",
        "Content-Type": "application/json",
    }

def default_header_with_token(token) -> dict:
    header = default_header()
    header.update(dict(Authorization=f"Bearer {token}"))
    return header

def default_header_with_x_token(token) -> dict:
    header = default_header()
    header.update({"x-token": f"{token}"})
    return header


@pytest.fixture()
def database_connection():
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(autouse=True)
def drop_users(database_connection):
    db = database_connection
    try:
        _ = db.query(User).delete()
        db.commit()
    except:
        db.rollback()


@pytest.fixture()
def test_client():
    app = src.application.create_app()
    # FastAPI app startup/shutdown event is raised when entering/exiting this context
    with TestClient(app) as client:
        yield client


@pytest.fixture()
def valid_user_token(test_client):
    response = test_client.post(
        "/auth/signup",
        json={"username": "test_user", "email": "user@test.com", "password": "nah"},
        headers={"content-type": "application/json"},
    )
    assert response.status_code == 200
    yield response.json()["access_token"]
