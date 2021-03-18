from sqlalchemy.orm import Session

from cards_server.cards import sql_models, models
from cards_server.cards.models import WhiteCard, BlackCard


def add_new_white_card(db : Session, card : WhiteCard) -> sql_models.WhiteCard:
    db_card = sql_models.WhiteCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


def add_new_black_card(db: Session, card: BlackCard):
    db_card = sql_models.BlackCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card
