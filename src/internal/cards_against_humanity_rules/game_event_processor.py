from dataclasses import dataclass
from typing import Dict, Callable, Optional, Any

from sqlalchemy.orm import Session

from src.internal.cards_against_humanity_rules.game_factory import GameFactory
from src.internal.cards_against_humanity_rules.game_related_exceptions import (
    LogicalError,
)

from src.internal.cards_against_humanity_rules.models import (
    GameEvent,
    PlayerSubmitCards,
    SelectWinningSubmission,
    AdvanceRoundAfterVoting,
    GamePreferences,
)


@dataclass
class Reaction:
    event_callback: Callable
    validation: Optional[Callable] = None


class GameEventProcessor:
    def __init__(
        self,
        room_name,
        db: Session,
        preferences: GamePreferences,
    ):
        self.session = GameFactory.new_session(
            room_name, db=db, preferences=preferences
        )
        self.event_mapping: Dict[Any, Reaction] = {
            PlayerSubmitCards.event_id(): Reaction(
                event_callback=self.session.player_submit_card
            ),
            SelectWinningSubmission.event_id(): Reaction(
                event_callback=self.session.select_winner,
            ),
        }

    def on_new_event(self, event: GameEvent, sender_name: str):
        if isinstance(event, PlayerSubmitCards):
            self.session.player_submit_card(event)
        if isinstance(event, SelectWinningSubmission):
            self.session.select_winner(sender_name=sender_name, winner=event)
        if isinstance(event, AdvanceRoundAfterVoting):
            self.session.advance_after_voting()
        self.session.save()

    def event_loop(self):
        pass


class GameEventMapper:
    def __init__(self):
        self.mapping: Dict[str, GameEventProcessor] = {}

    def get_game(self, room_name) -> Optional[GameEventProcessor]:
        return self.mapping.get(room_name)

    def new_game(
        self, room_name: str, db: Session, preferences: GamePreferences
    ) -> GameEventProcessor:
        self.mapping[room_name] = GameEventProcessor(room_name, db, preferences)
        created_room = self.get_game(room_name)
        if created_room is None:
            raise LogicalError(
                "What? I have just created a game, but it does not exist?!"
            )
        return created_room

    def end_game(self, room_name):
        self.mapping.pop(room_name)
