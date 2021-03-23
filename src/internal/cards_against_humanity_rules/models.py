from typing import List

from pydantic import BaseModel, Field

from src.cards.models import BlackCard, WhiteCard
from src.internal.cards_against_humanity_rules.game_related_exceptions import (
    GameHasEnded,
)

CARDS_IN_PLAYER_HAND = 8
POINTS_TO_WIN = 10


class CardsAgainstHumanityRoles:
    PLAYER = "PLAYER"
    TZAR = "TZAR"


class GameStates:
    STARTING = "STARTING"
    PLAYERS_SUBMITTING_CARDS = "PLAYERS_SUBMITTING_CARDS"
    TZAR_CHOOSING_WINNER = "TZAR_CHOOSING_WINNER"


class Submission(BaseModel):
    black_card: BlackCard
    white_cards: List[WhiteCard]

    def __hash__(self):
        return hash(str(self.dict()))


class GameEvent(BaseModel):
    pass


class PlayerSubmitCards(GameEvent):
    submitting_user: str
    cards: List[WhiteCard]


class SelectWinningSubmission(GameEvent):
    submission: Submission


class CardsAgainstHumanityPlayer(BaseModel):
    username: str
    cards_in_hand: List[WhiteCard]
    points: int = 0
    current_role: str = CardsAgainstHumanityRoles.PLAYER

    submissions: List[Submission] = Field(default_factory=list)

    def __hash__(self):
        return hash(str(self.dict()))

    def elect_as_tzar(self):
        self.current_role = CardsAgainstHumanityRoles.TZAR
        print(f"{self.username} was elected az a TZAR")

    def revert_to_normal_player(self):
        self.current_role = CardsAgainstHumanityRoles.PLAYER

    def reward_points(self, points: int = 1):
        self.points += points
        print(f"{self.username} was given {points} points")
        if self.points >= POINTS_TO_WIN:
            raise GameHasEnded(
                f"Game has ended as {self.username} has reached {POINTS_TO_WIN} points"
            )
