from src.cards import models
from src.database import database_models


def test_white_card_model_conversion():
    mwc = models.WhiteCard(card_id=1, text="asd", icon="dsa", deck="whatevs")
    sql_white_card = database_models.WhiteCard(**mwc.dict())
    assert mwc.card_id == sql_white_card.card_id
    assert mwc.deck == sql_white_card.deck
    assert mwc.text == sql_white_card.text
    assert mwc.icon == sql_white_card.icon
