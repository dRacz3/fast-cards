import json

from sqlalchemy.orm.session import Session

from src.cards.crud import add_multiple_new_white_card, add_multiple_new_black_card
from src.cards.models import WhiteCard, BlackCard


def load_cards_to_dabase(db: Session, input_file_path: str):
    with open(input_file_path) as f:
        data = json.load(f)
    print("Inserting white cards")
    suc = 0
    fail = 0

    wcs = []
    for i, key in enumerate(data["white"]):
        wcs.append(WhiteCard(card_id=None, **key))

    try:
        add_multiple_new_white_card(db, wcs)
    except Exception as e:
        print(e)
        db.rollback()

    print(f"success:{suc},  failure: {fail}")

    print("Inserting black cards")
    bcs = []
    for i, key in enumerate(data["black"]):
        bcs.append(BlackCard(card_id=None, **key))
    try:
        add_multiple_new_black_card(db, bcs)
    except Exception as e:
        print(e)
        db.rollback()

    print(f"success:{ suc},  failure: {fail}")
