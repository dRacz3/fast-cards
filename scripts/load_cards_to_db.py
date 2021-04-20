from src.database.database import SessionLocal
from src.utils.bootstrapping import load_hungarian_cards_to_dabase

if __name__ == "__main__":
    database = SessionLocal()
    load_hungarian_cards_to_dabase(database, "resources/hungarian_cards.json")
