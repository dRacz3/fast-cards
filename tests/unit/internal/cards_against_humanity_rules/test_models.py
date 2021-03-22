from typing import List

from src.internal.cards_against_humanity_rules.models import (
    GameSession,
    CARDS_IN_PLAYER_HAND,
    GameStates,
    CardsAgainstHumanityRoles,
    CardsAgainstHumanityPlayer,
    Submission,
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


def test_game_starts_only_with_enough_players(
    database_connection, prefill_cards_to_database
):
    prefill_cards_to_database()
    db = database_connection
    sess = GameSession.new_session("test", 5, db)

    assert not sess.start_game()
    assert sess.state == GameStates.STARTING

    sess.player_join("Joe")
    sess.player_join("David")
    sess.player_join("Peter")

    assert sess.start_game()
    assert sess.state == GameStates.PLAYERS_SUBMITTING_CARDS

    assert sess.currently_active_card.pick is not None

    tzars = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.TZAR
    ]
    assert len(tzars) == 1
    the_tzar = tzars[0]

    everyone_else: List[CardsAgainstHumanityPlayer] = [
        p for p in sess.players if p.current_role == CardsAgainstHumanityRoles.PLAYER
    ]

    active_card_picks = sess.currently_active_card.pick
    for player in everyone_else:
        assert len(player.cards_in_hand) == CARDS_IN_PLAYER_HAND
        sess.player_submit_card(
            player.username, player.cards_in_hand[0:active_card_picks]
        )
        assert len(player.cards_in_hand) == CARDS_IN_PLAYER_HAND - active_card_picks

    assert sess.state == GameStates.TZAR_CHOOSING_WINNER
    the_winner_player: CardsAgainstHumanityPlayer = everyone_else[0]
    winning_submission = the_winner_player.submissions[-1]

    sess.select_winner(winning_submission)

    for p in everyone_else:
        if p != the_winner_player:
            assert p.points == 0
        else:
            assert p.points == 1
