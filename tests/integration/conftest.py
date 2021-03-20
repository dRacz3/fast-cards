from typing import Any

import pytest
from sqlalchemy.orm import Session

from src.database.database import SessionLocal


@pytest.fixture()
def database_connection():
    db = SessionLocal()
    yield db
    db.close()


def drop_table_content(db: Session, table_model: Any):
    try:
        _ = db.query(table_model).delete()
        db.commit()
    except:
        db.rollback()
