import json

from sqlalchemy.orm.session import Session

from src.cards.crud import (
    add_multiple_new_white_card,
    add_multiple_new_black_card,
    add_new_deck,
)
from src.cards.models import WhiteCard, BlackCard, DeckMetaData


def load_hungarian_cards_to_dabase(db: Session, input_file_path: str):
    with open(input_file_path) as f:
        data = json.load(f)

    wcs = []
    for i, key in enumerate(data["white"]):
        wcs.append(WhiteCard(card_id=None, **key))

    try:
        add_multiple_new_white_card(db, wcs)
    except Exception as e:
        print(e)
        db.rollback()

    bcs = []
    for i, key in enumerate(data["black"]):
        bcs.append(BlackCard(card_id=None, **key))
    try:
        add_multiple_new_black_card(db, bcs)
    except Exception as e:
        print(e)
        db.rollback()


def load_offical_decks_to_game(
    database: Session, input_file_path, deck_limit: int = None
):
    with open(input_file_path, "r") as f:
        data = json.load(f)

    if deck_limit is not None:
        data = data[0 : min(len(data), deck_limit)]

    for pack in data:
        deck_name = pack["name"]
        print(f"Processing {deck_name}")

        add_new_deck(
            database,
            DeckMetaData(
                id_name=deck_name,
                description=deck_name,
                official=pack["official"],
                name=deck_name,
                icon=deck_name,
            ),
        )

        white_cards = []
        black_cards = []
        for w in pack["white"]:
            white_cards.append(
                WhiteCard(text=w["text"], icon=deck_name, deck=deck_name)
            )
        add_multiple_new_white_card(database, white_cards)

        for b in pack["black"]:
            black_cards.append(
                BlackCard(
                    text=b["text"], icon=deck_name, deck=deck_name, pick=b["pick"]
                )
            )
        add_multiple_new_black_card(database, black_cards)
