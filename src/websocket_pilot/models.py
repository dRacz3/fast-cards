from typing import List

from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.auth.models import UserSchema
from src.database import database_models


class Room(BaseModel):
    room_name: str
    host_user: UserSchema

    class Config:
        orm_mode = True

    @classmethod
    def query_all_room(cls, db : Session):
        rooms_returned : List[database_models.Room]  = db.query(database_models.Room).all()
        return [cls(room_name=r.room_name, host_user=r.host_user) for r in rooms_returned]

    @classmethod
    def create_room(cls, db: Session, room_name : str, creator : str):
        created_room_db = database_models.Room(room_name=room_name, host_user=creator)
        db.add(created_room_db)
        db.commit()
        db.refresh(created_room_db)
        return created_room_db