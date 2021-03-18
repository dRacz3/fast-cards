from sqlalchemy import Column, Integer, String, Boolean

from src.database.database import Base


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
