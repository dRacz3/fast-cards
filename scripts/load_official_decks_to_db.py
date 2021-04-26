import json

from src.cards.crud import (
    add_multiple_new_white_card,
    add_multiple_new_black_card,
    add_new_deck,
)
from src.cards.models import WhiteCard, BlackCard, DeckMetaData
from src.database.database import SessionLocal


if __name__ == "__main__":
    database = SessionLocal()
    with open("resources/official-decks.json", "r") as f:
        data = json.load(f)

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
