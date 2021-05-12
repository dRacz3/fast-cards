from src.database.database import SessionLocal
from src.utils.bootstrapping import load_offical_decks_to_game

if __name__ == "__main__":
    database = SessionLocal()

    file = "resources/official-decks.json"
    load_offical_decks_to_game(database, file)