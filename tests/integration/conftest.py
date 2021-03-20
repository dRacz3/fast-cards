import pytest

from src.database.database import SessionLocal


@pytest.fixture()
def database_connection():
    db = SessionLocal()
    yield db
    db.close()
