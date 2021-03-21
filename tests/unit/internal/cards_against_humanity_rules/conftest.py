import pytest

from scripts.load_cards_to_db import load_cards_to_dabase


@pytest.fixture()
def prefill_cards_to_database(database_connection):
    def _load():
        db = database_connection
        load_cards_to_dabase(db, "resources/hungarian_cards.json")
        return

    yield _load
