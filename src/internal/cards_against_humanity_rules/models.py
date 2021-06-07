from typing import List, Optional

from pydantic import BaseModel, Field

from src.cards.models import BlackCard, WhiteCard, DeckMetaData
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
    PLAYERS_INSPECTING_RESULT = "PLAYERS_INSPECTING_RESULT"
    FINISHED = "FINISHED"

class GameModes:
    NORMAL = "NORMAL"
    GOD_IS_DEAD = "GOD_IS_DEAD"


class Submission(BaseModel):
    black_card: BlackCard
    white_cards: List[WhiteCard]

    def __hash__(self):
        return hash(str(self.dict()))


class GameEvent(BaseModel):
    pass

    @staticmethod
    def event_id() -> int:
        return -1


class PlayerSubmitCards(GameEvent):
    submitting_user: str
    cards: List[WhiteCard]

    @staticmethod
    def event_id() -> int:
        return 1


class SelectWinningSubmission(GameEvent):
    submission: Submission

    @staticmethod
    def event_id() -> int:
        return 2

    def __hash__(self):
        return hash(str(self.dict()))

    def __str__(self):
        combos = self.submission.black_card.text.split("_")
        return (
            f"{list(zip(combos, [card.text for card in self.submission.white_cards]))}"
        )

    def __repr__(self):
        return self.__str__()


class AdvanceRoundAfterVoting(GameEvent):
    @staticmethod
    def event_id() -> int:
        return 3


class CardsAgainstHumanityPlayer(BaseModel):
    username: str
    cards_in_hand: List[WhiteCard]
    points: int = 0
    current_role: str = CardsAgainstHumanityRoles.PLAYER

    submissions: List[Submission] = Field(default_factory=list)
    votes: List[SelectWinningSubmission] = Field(default_factory=list)

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


class LastWinnerInfo(BaseModel):
    username: str
    submission: Submission


class PlayerOutsideView(BaseModel):
    username: str
    points: int = 0
    current_role: str = CardsAgainstHumanityRoles.PLAYER
    submissions: List[Submission] = Field(default_factory=list)
    votes: List[SelectWinningSubmission] = Field(default_factory=list)

    @classmethod
    def from_player(cls, player: CardsAgainstHumanityPlayer):
        p = player.copy(exclude={"cards_in_hand"}).dict()
        return cls(**p)


class GamePreferences(BaseModel):
    deck_preferences: Optional[List[DeckMetaData]] = None
    points_needed_for_win: int = 10
    max_round_count: int = 15
    mode: str = GameModes.NORMAL

    @classmethod
    def default(cls):
        return cls()

    @classmethod
    def hungarian(cls):
        return cls(
            deck_preferences=[
                DeckMetaData(
                    id_name="hungarian",
                    description="Hungarian card collection",
                    official=False,
                    name="hungarian",
                    icon="hungarian",
                )
            ],
        )

    @classmethod
    def god_is_dead_mode(cls):
        return cls(mode=GameModes.GOD_IS_DEAD)
