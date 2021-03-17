from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import DATABASE_BACKEND

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

if "SQLITE" == DATABASE_BACKEND:
    # this is needed only for SQLite. It's not needed for other databases
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={**connect_args})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
