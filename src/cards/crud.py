import logging
import random
from typing import List, Optional

from sqlalchemy.orm import Session

from src.database import database_models
from src.cards.models import WhiteCard, BlackCard, DeckMetaData

logger = logging.getLogger('crud-ops')

def add_new_white_card(db: Session, card: WhiteCard) -> database_models.WhiteCard:
    db_card = database_models.WhiteCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    logger.info(f"Added {card} to database")
    return db_card


def add_multiple_new_white_card(
    db: Session, cards: List[WhiteCard]
) -> List[database_models.WhiteCard]:
    db_cards = [database_models.WhiteCard(**card.dict()) for card in cards]
    db.add_all(db_cards)
    db.commit()
    [db.refresh(c) for c in db_cards]
    logger.info(f"Added {cards} to database")
    return db_cards


def add_new_black_card(db: Session, card: BlackCard) -> database_models.BlackCard:
    db_card = database_models.BlackCard(**card.dict())
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    logger.info(f"Added {card} to database")
    return db_card


def add_new_deck(db: Session, deck: DeckMetaData) -> database_models.BlackCard:
    db_deck = database_models.DeckMetaData(**deck.dict())
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    logger.info(f"Added {deck} to database")
    return db_deck


def add_multiple_new_black_card(
    db: Session, cards: List[BlackCard]
) -> List[database_models.BlackCard]:
    db_cards = [database_models.BlackCard(**card.dict()) for card in cards]
    db.add_all(db_cards)
    db.commit()
    [db.refresh(c) for c in db_cards]
    logger.info(f"Added {cards} to database")
    return db_cards


def get_n_random_white_cards(
    db: Session, count: int, allowed_decks: Optional[List[DeckMetaData]] = None
) -> List[WhiteCard]:
    returned_cards: List[database_models.WhiteCard]
    if allowed_decks is None:
        returned_cards = db.query(database_models.WhiteCard).all()
    else:
        returned_cards = (
            db.query(database_models.WhiteCard)
            .filter(
                database_models.WhiteCard.deck.in_([d.id_name for d in allowed_decks])
            )
            .all()
        )
    selected = random.sample(returned_cards, count)
    return [
        WhiteCard(deck=c.deck, card_id=c.card_id, text=c.text, icon=c.icon)
        for c in selected
    ]


def get_n_random_black_cards(
    db: Session, count: int, allowed_decks: Optional[List[DeckMetaData]] = None
) -> List[BlackCard]:
    returned_cards: List[database_models.BlackCard]
    if allowed_decks is None:
        returned_cards = db.query(database_models.BlackCard).all()
    else:
        returned_cards = (
            db.query(database_models.BlackCard)
            .filter(
                database_models.BlackCard.deck.in_([d.id_name for d in allowed_decks])
            )
            .all()
        )

    selected = random.sample(returned_cards, count)
    return [
        BlackCard(deck=c.deck, card_id=c.card_id, text=c.text, icon=c.icon, pick=c.pick)
        for c in selected
    ]


def get_deck_list(db: Session) -> List[DeckMetaData]:
    decks_in_db: List[database_models.DeckMetaData] = db.query(
        database_models.DeckMetaData
    ).all()
    return [
        DeckMetaData(
            id_name=d.id_name,
            description=d.description,
            official=d.official,
            name=d.name,
            icon=d.icon,
        )
        for d in decks_in_db
    ]


def drop_all_cards(db: Session):
    logger.warning(f"Dropping all cards in database")
    for c in db.query(database_models.WhiteCard).all():
        db.delete(c)
    for b in db.query(database_models.BlackCard).all():
        db.delete(b)
    for d in db.query(database_models.DeckMetaData).all():
        db.delete(d)

    db.commit()
