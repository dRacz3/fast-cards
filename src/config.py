from functools import lru_cache
import os
from pydantic import BaseSettings


# Reminder:  BaseSettings props can be overwritten by env vars, even though it is not specified.
class Settings(BaseSettings):
    DATABASE_BACKEND: str = "SQLITE"
    RUNTIME_ENV: str = os.getenv("RUNTIME_ENV", "TEST")

    JWT_SECRET: str = os.getenv("JWT_SECRET", "seceret")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
