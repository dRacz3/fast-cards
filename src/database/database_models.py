from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

from .database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    # owner = relationship("User", back_populates="items")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)


class WhiteCard(Base):
    __tablename__ = "white_cards"

    card_id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    icon = Column(String)
    deck = Column(String, index=True)


class BlackCard(Base):
    __tablename__ = "black_cards"

    card_id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    icon = Column(String)
    deck = Column(String, index=True)
    pick = Column(Integer)