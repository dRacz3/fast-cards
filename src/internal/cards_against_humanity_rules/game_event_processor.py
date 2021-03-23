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


class GameEventMapper:
    def __init__(self):
        self.mapping: Dict[str, GameEventProcessor] = {}

    def new_game(self, session_name: str, db: Session):
        self.mapping[session_name] = GameEventProcessor(session_name, db)

    def end_game(self, session_name):
        self.mapping.pop(session_name)


@dataclass
class Reaction:
    event_callback: Callable
    validation: Optional[Callable] = None


class GameEventProcessor:
    def __init__(self, session_name, db: Session):
        self.session = GameStateMachine.new_session(session_name, round_count=3, db=db)
        self.event_mapping: Dict[Any, Reaction] = {
            PlayerSubmitCards: Reaction(event_callback=self.session.player_submit_card),
            SelectWinningSubmission: Reaction(
                event_callback=self.session.select_winner,
                validation=self.winner_select_validation,
            ),
        }

    def on_new_event(self, event: GameEvent, sendername: str):
        reaction: Reaction = self.event_mapping[event]
        if reaction.validation is not None:
            reaction.validation(event, sendername)
        return reaction.event_callback(event, sendername)

    def winner_select_validation(self, event: GameEvent, sendername: str):
        tzars = [
            p
            for p in self.session.players
            if p.current_role == CardsAgainstHumanityRoles.TZAR
        ]
        if len(tzars) != 1:
            raise LogicalError(f"There should be only one tzar. Current tzars: {tzars}")

        if tzars[0].username != sendername:
            raise LogicalError(
                f"{sendername} tried to select winner, but the tzar is {tzars[0]}"
            )
