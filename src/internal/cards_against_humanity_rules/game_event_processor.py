from dataclasses import dataclass
from typing import Dict, Callable, Optional, Any

from sqlalchemy.orm import Session

from src.internal.cards_against_humanity_rules.game_related_exceptions import (
    LogicalError,
)
from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStateMachine,
)
from src.internal.cards_against_humanity_rules.models import (
    GameEvent,
    PlayerSubmitCards,
    SelectWinningSubmission,
    CardsAgainstHumanityRoles,
)


@dataclass
class Reaction:
    event_callback: Callable
    validation: Optional[Callable] = None


class GameEventProcessor:
    def __init__(self, room_name, db: Session):
        self.session = GameStateMachine.new_session(room_name, round_count=3, db=db)
        self.event_mapping: Dict[Any, Reaction] = {
            PlayerSubmitCards: Reaction(event_callback=self.session.player_submit_card),
            SelectWinningSubmission: Reaction(
                event_callback=self.session.select_winner,
                validation=self.winner_select_validation,
            ),
        }

    def on_new_event(self, event: GameEvent, sender_name: str):
        reaction: Reaction = self.event_mapping[event]
        if reaction.validation is not None:
            reaction.validation(event, sender_name)
        return reaction.event_callback(event, sender_name)

    def winner_select_validation(self, event: GameEvent, sender_name: str):
        tzars = [
            p
            for p in self.session.players
            if p.current_role == CardsAgainstHumanityRoles.TZAR
        ]
        if len(tzars) != 1:
            raise LogicalError(f"There should be only one tzar. Current tzars: {tzars}")

        if tzars[0].username != sender_name:
            raise LogicalError(
                f"{sender_name} tried to select winner, but the tzar is {tzars[0]}"
            )


class GameEventMapper:
    def __init__(self):
        self.mapping: Dict[str, GameEventProcessor] = {}

    def get_game(self, room_name) -> GameEventProcessor:
        return self.mapping[room_name]

    def new_game(self, session_name: str, db: Session):
        self.mapping[session_name] = GameEventProcessor(session_name, db)

    def end_game(self, session_name):
        self.mapping.pop(session_name)
