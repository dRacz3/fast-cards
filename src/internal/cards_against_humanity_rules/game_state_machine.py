import random
from typing import List, Optional, Dict

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from src.cards.crud import get_n_random_white_cards, get_n_random_black_cards
from src.cards.models import BlackCard, WhiteCard
from src.internal.cards_against_humanity_rules.game_related_exceptions import (
    InvalidPlayerAction,
    LogicalError,
    GameHasEnded,
)
from src.internal.cards_against_humanity_rules.models import (
    GameStates,
    CardsAgainstHumanityPlayer,
    Submission,
    CARDS_IN_PLAYER_HAND,
    CardsAgainstHumanityRoles,
)


class GameStateMachine(BaseModel):
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

    def start_game(self) -> bool:
        if len(self.players) >= 2:
            self.players[0].elect_as_tzar()
            self.__next_active_black_card()
            self.state = GameStates.PLAYERS_SUBMITTING_CARDS
            return True
        else:
            return False

    def player_submit_card(self, username: str, cards: List[WhiteCard]):
        if self.currently_active_card is None:
            raise InvalidPlayerAction(
                "Game has not started, but player tried to submit cards."
            )

        player = self.__lookup_player_by_name(username)
        if player is not None:
            if len(cards) != self.currently_active_card.pick:
                raise InvalidPlayerAction(
                    f"{username} tried to submit {len(cards)}, but it should've been {self.currently_active_card.pick}"
                )

            verified_card_count = len([c for c in cards if c in player.cards_in_hand])
            if verified_card_count != len(cards):
                raise InvalidPlayerAction(
                    f"{username} tried to submit cards, that are not in hands!"
                )

            submission = Submission(
                white_cards=cards, black_card=self.currently_active_card
            )
            player.submissions.append(submission)
            self.player_submissions[player] = submission
            for card in cards:
                player.cards_in_hand.remove(card)

            if (
                len(self.player_submissions.keys()) == len(self.players) - 1
            ):  # -1 is the Tzar
                self.__close_round()

        else:
            raise LogicalError(
                f"Tried to lookup player: {username}, but was not found."
                f"Current player list : {self.players}"
            )

    def select_winner(self, selected_submission: Submission):
        for player, submission in self.player_submissions.items():
            if submission == selected_submission:
                player.reward_points(1)
                self.__start_new_round()
                return

        raise InvalidPlayerAction(
            f"Selected submission does not exist! "
            f"Selected: {selected_submission}, "
            f"Player submissions: {self.player_submissions}"
        )

    def __lookup_player_by_name(
        self, username: str
    ) -> Optional[CardsAgainstHumanityPlayer]:
        for p in self.players:
            if p.username == username:
                return p
        return None

    def __next_active_black_card(self):
        if len(self.black_cards) == 0:
            raise GameHasEnded("Game has ended, no more black cards left.")
        self.currently_active_card = self.black_cards.pop()

    def __close_round(self):
        self.state = GameStates.TZAR_CHOOSING_WINNER

    def __start_new_round(self):
        self.round_count += 1
        print(f"Starting a new round #{self.round_count}")
        self.player_submissions.clear()
        self.__next_active_black_card()
        for p in self.players:
            card_count: int = len(p.cards_in_hand)
            if card_count < CARDS_IN_PLAYER_HAND:
                required_card_count = CARDS_IN_PLAYER_HAND - card_count
                if required_card_count > len(self.white_cards):
                    raise GameHasEnded("No more white cards left")
                white_cards_for_player = self.white_cards[0:required_card_count]
                print(f"Adding cards to {p.username}=> {white_cards_for_player}")
                p.cards_in_hand += white_cards_for_player
                for c in white_cards_for_player:
                    self.white_cards.remove(c)
        self.__elect_new_tzar()

    def __elect_new_tzar(self):
        player = random.choice(
            [
                p
                for p in self.players
                if p.current_role != CardsAgainstHumanityRoles.TZAR
            ]
        )
        self.__revert_everyone_to_normal_player()
        player.elect_as_tzar()

    def __revert_everyone_to_normal_player(self):
        for p in self.players:
            p.revert_to_normal_player()

    @classmethod
    def new_session(cls, room_name: str, round_count: int, db: Session):
        return cls(
            room_name=room_name,
            white_cards=get_n_random_white_cards(db, round_count * 15),
            black_cards=get_n_random_black_cards(db, round_count),
        )

    def __hash__(self):
        return hash(str(self.dict()))
