from typing import List

from pydantic import BaseModel

from src.database.schema import Item


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    username : str
    password: str


class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
