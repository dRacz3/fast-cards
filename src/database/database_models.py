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


class BlackCard(Base):
    __tablename__ = "black_cards"

    card_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(String)
    icon = Column(String)
    deck = Column(String, index=True)
    pick = Column(Integer)
