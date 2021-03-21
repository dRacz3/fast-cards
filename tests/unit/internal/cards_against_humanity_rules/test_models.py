from src.internal.cards_against_humanity_rules.models import (
    GameSession,
    CARDS_IN_PLAYER_HAND,
)


def test_game_session_creation_and_user_assignment(
    database_connection, prefill_cards_to_database
):
    prefill_cards_to_database()
    db = database_connection
    sess = GameSession.new_session("test", 5, db)
    assert len(sess.players) == 0
    assert len(sess.black_cards) == 5
    assert len(sess.white_cards) > 15

    sess.player_join("Joe")
    sess.player_join("David")

    assert len(sess.players) == 2

    player_names = [p.username for p in sess.players]
    assert "Joe" in player_names
    assert "David" in player_names

    for p in sess.players:
        assert len(p.cards_in_hand) == CARDS_IN_PLAYER_HAND

    sess.player_leaves("David")
    assert len(sess.players) == 1
    player_names = [p.username for p in sess.players]
    assert "Joe" in player_names
