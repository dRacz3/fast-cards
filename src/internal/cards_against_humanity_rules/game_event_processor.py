from typing import Dict

from sqlalchemy.orm import Session

from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStateMachine,
)


class GameEventMapper:
    def __init__(self):
        self.mapping: Dict[str, GameEventProcessor] = {}

    def new_game(self, session_name: str, db: Session):
        self.mapping[session_name] = GameEventProcessor(session_name, db)

    def end_game(self, session_name):
        self.mapping.pop(session_name)


class GameEventProcessor:
    def __init__(self, session_name, db: Session):
        self.session = GameStateMachine.new_session(session_name, round_count=3, db=db)

    def on_new_event(self, event):
        # TODO: Act corresspondingly
        pass
