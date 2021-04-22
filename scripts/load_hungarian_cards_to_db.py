from src.cards.crud import add_new_deck
from src.cards.models import DeckMetaData
from src.database.database import SessionLocal
from src.utils.bootstrapping import load_hungarian_cards_to_dabase

if __name__ == "__main__":
    database = SessionLocal()
    add_new_deck(database, DeckMetaData(id_name='hungarian',
                                        description='Hungarian card collection',
                                        official=False,
                                        name='hungarian',
                                        icon='hungarian'))
    load_hungarian_cards_to_dabase(database, "resources/hungarian_cards.json")
