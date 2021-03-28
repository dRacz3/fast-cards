import random
from typing import List

from sqlalchemy.orm import Session

from src.database import database_models
from src.cards.models import WhiteCard, BlackCard


def add_new_white_card(db: Session, card: WhiteCard) -> database_models.WhiteCard:
    db_card = database_models.WhiteCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


def add_multiple_new_white_card(
    db: Session, cards: List[WhiteCard]
) -> List[database_models.WhiteCard]:
    db_cards = [database_models.WhiteCard(**card.dict()) for card in cards]
    db.add_all(db_cards)
    db.commit()
    [db.refresh(c) for c in db_cards]
    return db_cards


def add_new_black_card(db: Session, card: BlackCard) -> database_models.BlackCard:
    db_card = database_models.BlackCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


def add_multiple_new_black_card(
    db: Session, cards: List[BlackCard]
) -> List[database_models.BlackCard]:
    db_cards = [database_models.BlackCard(**card.dict()) for card in cards]
    db.add_all(db_cards)
    db.commit()
    [db.refresh(c) for c in db_cards]
    return db_cards


def get_n_random_white_cards(db: Session, count: int) -> List[WhiteCard]:
    returned_cards: List[database_models.WhiteCard] = db.query(
        database_models.WhiteCard
    ).all()
    selected = random.sample(returned_cards, count)
    return [
        WhiteCard(deck=c.deck, card_id=c.card_id, text=c.text, icon=c.icon)
        for c in selected
    ]


def get_n_random_black_cards(db: Session, count: int) -> List[BlackCard]:
    returned_cards: List[database_models.BlackCard] = db.query(
        database_models.BlackCard
    ).all()
    selected = random.sample(returned_cards, count)
    return [
        BlackCard(deck=c.deck, card_id=c.card_id, text=c.text, icon=c.icon, pick=c.pick)
        for c in selected
    ]
