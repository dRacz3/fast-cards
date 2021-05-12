from sqlalchemy.orm import Session

from src.cards.crud import get_n_random_white_cards, get_n_random_black_cards
from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStateMachine,
)
from src.internal.cards_against_humanity_rules.god_is_dead_mode_state_machine import (
    GodIsDeadModeStateMachine,
)
from src.internal.cards_against_humanity_rules.models import GamePreferences, GameModes


class GameFactory:
    @staticmethod
    def new_session(room_name: str, db: Session, preferences: GamePreferences):

        round_count = preferences.max_round_count
        if preferences.mode == GameModes.GOD_IS_DEAD:
            return GodIsDeadModeStateMachine(
                room_name=room_name,
                white_cards=get_n_random_white_cards(
                    db, round_count * 15, allowed_decks=preferences.deck_preferences
                ),
                black_cards=get_n_random_black_cards(
                    db, round_count * 3, allowed_decks=preferences.deck_preferences
                ),
            )
        else:
            return GameStateMachine(
                room_name=room_name,
                white_cards=get_n_random_white_cards(
                    db, round_count * 15, allowed_decks=preferences.deck_preferences
                ),
                black_cards=get_n_random_black_cards(
                    db, round_count * 3, allowed_decks=preferences.deck_preferences
                ),
            )
