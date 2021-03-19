from sqlalchemy.orm import Session

from src.database import database_models
from src.cards.models import WhiteCard, BlackCard


def add_new_white_card(db: Session, card: WhiteCard) -> database_models.WhiteCard:
    db_card = database_models.WhiteCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


def add_new_black_card(db: Session, card: BlackCard) -> database_models.BlackCard:
    db_card = database_models.BlackCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card
