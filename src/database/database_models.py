from sqlalchemy import Column, Integer, String, Boolean

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class WhiteCard(Base):
    __tablename__ = "white_cards"

    card_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(String)
    icon = Column(String)
    deck = Column(String, index=True)
    source = Column(String, default="LOADED")


class BlackCard(Base):
    __tablename__ = "black_cards"

    card_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(String)
    icon = Column(String)
    deck = Column(String, index=True)
    pick = Column(Integer)

    source = Column(String, default="LOADED")


class DeckMetaData(Base):
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_name = Column(String, unique=True)
    description = Column(String, unique=True)
    name = Column(String, unique=True)
    icon = Column(String)
    official = Column(Boolean)
    source = Column(String, default="LOADED")