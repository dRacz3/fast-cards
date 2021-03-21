from typing import List, Optional, Dict

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.cards.models import BlackCard, WhiteCard

from src.cards.crud import get_n_random_white_cards, get_n_random_black_cards

CARDS_IN_PLAYER_HAND = 8


class FatalException(Exception):
    pass


class GameEventException(Exception):
    pass


class PlayerHasWon(GameEventException):
    pass


class GameHasEnded(GameEventException):
    pass


class GameIsFull(GameEventException):
    pass


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


class CardsAgainstHumanityPlayer(BaseModel):
    username: str
    cards_in_hand: List[WhiteCard]
    points: int = 0
    current_role: str = CardsAgainstHumanityRoles.PLAYER

    submissions: List[Submission] = Field(default_factory=list)

    def elect_as_tzar(self):
        self.current_role = CardsAgainstHumanityRoles.TZAR

    def revert_to_normal_player(self):
        self.current_role = CardsAgainstHumanityRoles.PLAYER

    def reward_points(self, points=1):
        self.points += points
        if self.points > 5:
            raise PlayerHasWon(self)


class GameSession(BaseModel):
    room_name: str

    black_cards: List[BlackCard]
    white_cards: List[WhiteCard]

    state: str = GameStates.STARTING
    round_count: int = 0

    currently_active_card: Optional[BlackCard] = None
    players: List[CardsAgainstHumanityPlayer] = Field(default_factory=list)
    player_submissions: Dict[CardsAgainstHumanityPlayer, Submission] = Field(
        default_factory=dict
    )

    def __lookup_player_by_name(
        self, username: str
    ) -> Optional[CardsAgainstHumanityPlayer]:
        for p in self.players:
            if p.username == username:
                return p
        return None

    def player_join(self, username: str):
        white_cards_for_player = self.white_cards[0:CARDS_IN_PLAYER_HAND]

        new_player = CardsAgainstHumanityPlayer(
            username=username, cards_in_hand=white_cards_for_player, points=0
        )
        for c in white_cards_for_player:
            self.white_cards.remove(c)

        self.players.append(new_player)

    def player_leaves(self, username: str):
        player_to_remove = None
        for p in self.players:
            if p.username == username:
                player_to_remove = p
        if player_to_remove is not None:
            self.players.remove(player_to_remove)

    def start_game(self):
        if len(self.players) > 2:
            self.players[0].elect_as_tzar()
            self.state = GameStates.PLAYERS_SUBMITTING_CARDS

    def player_submit_card(self, username: str, cards: List[WhiteCard]):
        player = self.__lookup_player_by_name(username)
        if player is not None:
            self.player_submissions[player] = Submission(
                white_cards=cards, black_card=self.currently_active_card
            )
        else:
            FatalException(
                f"Tried to lookup player: {username}, but was not found. Current player list : {self.players}"
            )

    @classmethod
    def new_session(cls, room_name: str, round_count: int, db: Session):
        return cls(
            room_name=room_name,
            white_cards=get_n_random_white_cards(db, round_count * 15),
            black_cards=get_n_random_black_cards(db, round_count),
        )
