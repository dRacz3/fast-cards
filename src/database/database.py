from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import get_settings

# TODO: move it to settings on a better day.
if get_settings().RUNTIME_ENV == "TEST":
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sql_app.db"
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./prod_sql_app.db"

if "SQLITE" == get_settings().DATABASE_BACKEND:
    # this is needed only for SQLite. It's not needed for other databases
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={**connect_args})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
