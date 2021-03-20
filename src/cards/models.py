from typing import Optional

from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module


class DeckMetaData(BaseModel):
    id_name: str
    description: str
    official: bool = False
    name: str
    icon: str

    class Config:
        orm_mode = True


class BlackCard(BaseModel):
    card_id: Optional[int] = -1
    text: str
    icon: str
    deck: str
    pick: int

    class Config:
        orm_mode = True


class WhiteCard(BaseModel):
    card_id: Optional[int] = -1
    text: str
    icon: str
    deck: str

    class Config:
        orm_mode = True
