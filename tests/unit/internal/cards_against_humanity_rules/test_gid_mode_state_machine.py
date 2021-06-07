import pytest

from src.internal.cards_against_humanity_rules.game_factory import GameFactory
from src.internal.cards_against_humanity_rules.game_related_exceptions import (
    GameHasEnded,
    InvalidPlayerAction,
)
from src.internal.cards_against_humanity_rules.god_is_dead_mode_state_machine import (
    GodIsDeadModeStateMachine,
)
from src.internal.cards_against_humanity_rules.models import (
    GameModes,
    GamePreferences,
    PlayerSubmitCards,
    SelectWinningSubmission,
    Submission,
)


def test_default_props():
    sm = GodIsDeadModeStateMachine(room_name="", black_cards=[], white_cards=[])
    assert sm.mode == GameModes.GOD_IS_DEAD
    assert sm.winner_votes == {}
    assert sm.tzar() is None


def test_player_select_winner_behaviour(
    database_connection, prefill_official_cards_to_database
):
    """
        room_name: str,
        round_count: int,
        db: Session,
        preferences: GamePreferences,
    :return:
    """
    prefill_official_cards_to_database()

    sm = GameFactory.new_session(
        room_name="test room",
        db=database_connection,
        preferences=GamePreferences.god_is_dead_mode(),
    )

    assert isinstance(sm, GodIsDeadModeStateMachine)
    players = ["P1", "P2", "P3"]
    for p in players:
        sm.player_join(p)

    assert len(sm.players) == 3
    assert sm.tzar() is None
    sm.start_game()

    with pytest.raises(GameHasEnded):
        for i in range(15):
            to_pick = sm.currently_active_card.pick

            submissions = {}
            for p in players:
                cards_to_submit = sm.player_lookup[p].cards_in_hand[0:to_pick]
                submissions[p] = cards_to_submit
                sm.player_submit_card(
                    PlayerSubmitCards(submitting_user=p, cards=cards_to_submit)
                )

            for p in players:
                sub = Submission(
                    black_card=sm.currently_active_card,
                    white_cards=submissions[list(submissions.keys())[0]],
                )
                sws = SelectWinningSubmission(submission=sub)
                sm.select_winner(
                    sender_name=p,
                    winner=sws,
                )
            sm.advance_after_voting()

            assert sm.player_lookup[players[0]].points == i + 1
    assert sm.player_lookup[players[0]].points == 10
    assert sm.player_lookup[players[1]].points == 0
    assert sm.player_lookup[players[2]].points == 0


def test_player_advance_after_winner_raises_exception_when_submitted_invalidly(
    database_connection, prefill_official_cards_to_database
):
    """
        room_name: str,
        round_count: int,
        db: Session,
        preferences: GamePreferences,
    :return:
    """
    prefill_official_cards_to_database()

    sm = GameFactory.new_session(
        room_name="test room",
        db=database_connection,
        preferences=GamePreferences.god_is_dead_mode(),
    )

    assert isinstance(sm, GodIsDeadModeStateMachine)
    players = ["P1", "P2", "P3"]
    for p in players:
        sm.player_join(p)

    assert len(sm.players) == 3
    assert sm.tzar() is None
    sm.start_game()

    to_pick = sm.currently_active_card.pick

    submissions = {}
    for p in players:
        cards_to_submit = sm.player_lookup[p].cards_in_hand[0:to_pick]
        submissions[p] = cards_to_submit
        sm.player_submit_card(
            PlayerSubmitCards(submitting_user=p, cards=cards_to_submit)
        )

    for p in players:
        sub = Submission(
            black_card=sm.currently_active_card,
            white_cards=submissions[list(submissions.keys())[0]],
        )
        sws = SelectWinningSubmission(submission=sub)
        sm.select_winner(
            sender_name=p,
            winner=sws,
        )

        # Only the last advance is valid
        if p != players[-1]:
            with pytest.raises(InvalidPlayerAction):
                print(f"{p} votes")
                sm.advance_after_voting()
        else:
            sm.advance_after_voting()
