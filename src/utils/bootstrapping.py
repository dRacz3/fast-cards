import json

from sqlalchemy.orm.session import Session

from src.cards.crud import add_multiple_new_white_card, add_multiple_new_black_card
from src.cards.models import WhiteCard, BlackCard


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
