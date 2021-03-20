import pytest

from src.cards.crud import add_new_white_card, add_new_black_card

from src.cards.models import WhiteCard, BlackCard
from src.database import database_models
from tests.conftest import drop_table_content


@pytest.fixture()
def clean_white_cards(database_connection):
    drop_table_content(database_connection, database_models.WhiteCard)


@pytest.fixture()
def clean_black_cards(database_connection):
    drop_table_content(database_connection, database_models.BlackCard)


def test_add_new_white_card(database_connection, clean_white_cards):
    db = database_connection
    assert len(db.query(database_models.WhiteCard).all()) == 0
    white_card_to_insert = WhiteCard(
        card_id=15, text="testtext", icon="asd", deck="nonexistent"
    )
    added_card = add_new_white_card(db, white_card_to_insert)
    all_cards = db.query(database_models.WhiteCard).all()
    assert added_card in all_cards


def test_add_new_black_card(database_connection, clean_black_cards):
    db = database_connection
    assert len(db.query(database_models.BlackCard).all()) == 0
    black_card_to_insert = BlackCard(
        card_id=15, text="testtext _ asd _", icon="asd", deck="nonexistent", pick=2
    )
    added_card = add_new_black_card(db, black_card_to_insert)
    all_cards = db.query(database_models.BlackCard).all()
    assert added_card in all_cards
