from src.internal.cards_against_humanity_rules.game_factory import GameFactory
from src.internal.cards_against_humanity_rules.god_is_dead_mode_state_machine import (
    GodIsDeadModeStateMachine,
)
from src.internal.cards_against_humanity_rules.models import GameModes, GamePreferences


def test_default_props():
    sm = GodIsDeadModeStateMachine(room_name="", black_cards=[], white_cards=[])
    assert sm.mode == GameModes.GOD_IS_DEAD
    assert sm.winner_votes == {}
    assert sm.tzar() is None


def test_player_select_winner_behaviour(database_connection):
    """
        room_name: str,
        round_count: int,
        db: Session,
        preferences: GamePreferences,
    :return:
    """
    GameFactory.new_session(
        room_name="test room",
        round_count=2,
        db=database_connection,
        preferences=GamePreferences.god_is_dead_mode(),
    )
