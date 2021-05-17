import json
import logging
import os
import random
from typing import List, Optional, Dict, Union

from pydantic import BaseModel, Field

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
    PlayerSubmitCards,
    SelectWinningSubmission,
    PlayerOutsideView,
    LastWinnerInfo,
    GameModes,
)


class GameStateMachine(BaseModel):
    room_name: str

    black_cards: List[BlackCard]
    white_cards: List[WhiteCard]

    state: str = GameStates.STARTING
    mode: str = GameModes.NORMAL
    last_winners: Optional[List[LastWinnerInfo]]
    round_count: int = 0

    currently_active_card: Optional[BlackCard] = None
    player_submissions: Dict[str, Submission] = Field(default_factory=dict)

    player_lookup: Dict[str, CardsAgainstHumanityPlayer] = Field(default_factory=dict)

    @property
    def logger(self):
        return logging.getLogger(f"room-[{self.room_name}]")


    @property
    def players(self) -> List[CardsAgainstHumanityPlayer]:
        return list(self.player_lookup.values())

    @property
    def tzar(self) -> Optional[CardsAgainstHumanityPlayer]:
        # Untested
        # Unused
        tzars = [
            p for p in self.players if p.current_role == CardsAgainstHumanityRoles.TZAR
        ]
        if len(tzars) == 1:
            return tzars[0]
        elif len(tzars) > 1:
            raise LogicalError(f"Cannot be more than 1 Tzar! Current tzars: {tzars}")
        return None

    def player_join(self, username: str):
        if self.player_lookup.get(username) is None:
            white_cards_for_player = self.white_cards[0:CARDS_IN_PLAYER_HAND]

            new_player = CardsAgainstHumanityPlayer(
                username=username, cards_in_hand=white_cards_for_player, points=0
            )
            for c in white_cards_for_player:
                self.white_cards.remove(c)

            self.player_lookup[new_player.username] = new_player

    def player_leaves(self, username: str):
        player_to_remove = None
        for p in self.players:
            if p.username == username:
                player_to_remove = p

        if self.tzar == player_to_remove:
            self.logger.info("The tzar is removed.. Starting a new round")
            self.__start_new_round()
        if player_to_remove is not None:
            self.player_lookup.pop(player_to_remove.username)

    def start_game(self):
        if len(self.players) >= 2:
            self._elect_new_tzar()
            self.__next_active_black_card()
            self.state = GameStates.PLAYERS_SUBMITTING_CARDS
            self.save()
        else:
            raise InvalidPlayerAction(
                f"Game cannot be started without enough players!. Current players: {self.player_lookup}"
            )

    def player_submit_card(self, submit_event: PlayerSubmitCards):
        if self.currently_active_card is None:
            raise InvalidPlayerAction(
                "Game has not started, but player tried to submit cards."
            )

        player = self.__lookup_player_by_name(submit_event.submitting_user)
        if player is not None:
            if len(submit_event.cards) != self.currently_active_card.pick:
                raise InvalidPlayerAction(
                    f"{submit_event.submitting_user} tried to submit {len(submit_event.cards)}, but it should've been {self.currently_active_card.pick}"
                )

            verified_card_count = len(
                [c for c in submit_event.cards if c in player.cards_in_hand]
            )
            if verified_card_count != len(submit_event.cards):
                raise InvalidPlayerAction(
                    f"{submit_event.submitting_user} tried to submit cards, that are not in hands!"
                )

            if self.player_submissions.get(player.username) is not None:
                # Potential optimization here, could replace the submission,
                # and return cards to user hand from previous submission, allowing to overwrite it.
                # For now its not possible.
                raise InvalidPlayerAction(
                    f"{submit_event.submitting_user} tried to submit cards more than once."
                )

            submission = Submission(
                white_cards=submit_event.cards, black_card=self.currently_active_card
            )
            player.submissions.append(submission)
            self.player_submissions[player.username] = submission
            for card in submit_event.cards:
                player.cards_in_hand.remove(card)

            self._advance()

        else:
            raise LogicalError(
                f"Tried to lookup player: {submit_event.submitting_user}, but was not found."
                f"Current player list : {self.players}"
            )

    def _advance(self):
        if len(self.player_submissions.keys()) == len(self.players) - 1:
            self._close_round()

    def select_winner(self, sender_name, winner: SelectWinningSubmission):
        tzars = [
            p for p in self.players if p.current_role == CardsAgainstHumanityRoles.TZAR
        ]
        if len(tzars) != 1:
            raise LogicalError(f"There should be only one tzar. Current tzars: {tzars}")

        if tzars[0].username != sender_name:
            raise LogicalError(
                f"{sender_name} tried to select winner, but the tzar is {tzars[0]}"
            )
        return self._select_winner(winner)

    def _select_winner(
        self, winners: Union[SelectWinningSubmission, List[SelectWinningSubmission]]
    ):
        if not isinstance(winners, List):
            winners = [winners]

        last_winners = []

        # TODO : nicer pls..
        game_has_ended = False
        game_end_reason = ""
        if len(winners) > 0:
            for winner in winners:
                for username, submission in self.player_submissions.items():
                    if submission == winner.submission:
                        player = self.__lookup_player_by_name(username)
                        if player is None:
                            raise LogicalError(
                                "Selected submission belongs to a player that is not in the game anymore."
                            )
                        try:
                            player.reward_points(1)
                            last_winners.append(
                                LastWinnerInfo(
                                    username=player.username,
                                    submission=winner.submission,
                                )
                            )
                        # This may yield a bug, when 2 players have the same score each.
                        # And both shall receive a same point. TODO: Fix multiple winners bug
                        except GameHasEnded as e:
                            game_has_ended = True
                            game_end_reason += f", {str(e)}"
            self.last_winners = last_winners

            if game_has_ended:
                self.__finish_game(game_end_reason)

            self.__start_new_round()

            if len(self.last_winners) == len(winners):
                return
            else:
                raise InvalidPlayerAction(
                    f"Number of winners does not match the expected."
                    f"Selected: {winners}, but really it is : {last_winners}"
                )

    def __lookup_player_by_name(
        self, username: str
    ) -> Optional[CardsAgainstHumanityPlayer]:
        return self.player_lookup.get(username)

    def __next_active_black_card(self):
        if len(self.black_cards) == 0:
            self.__finish_game("Game has ended, no more black cards left.")
        self.currently_active_card = self.black_cards.pop()

    def _close_round(self):
        self.save()
        self.state = GameStates.TZAR_CHOOSING_WINNER

    def __start_new_round(self):
        if self.state == GameStates.FINISHED:
            return
        self.round_count += 1
        self.logger.info(f"Starting a new round #{self.round_count}")
        self.state = GameStates.PLAYERS_SUBMITTING_CARDS
        self.player_submissions.clear()
        self.__next_active_black_card()
        for p in self.players:
            card_count: int = len(p.cards_in_hand)
            if card_count < CARDS_IN_PLAYER_HAND:
                required_card_count = CARDS_IN_PLAYER_HAND - card_count
                if required_card_count > len(self.white_cards):
                    break
                white_cards_for_player = self.white_cards[0:required_card_count]
                self.logger.info(f"Adding cards to {p.username}=> {white_cards_for_player}")
                p.cards_in_hand += white_cards_for_player
                for c in white_cards_for_player:
                    self.white_cards.remove(c)

        self._check_if_very_player_has_enough_cards(
            self.players, active_pick=self.currently_active_card.pick
        )
        self._elect_new_tzar()

    @staticmethod
    def _check_if_very_player_has_enough_cards(
        players: List[CardsAgainstHumanityPlayer], active_pick: int
    ):
        """
        Checks if every player has at least enough cards to play.
        :param players: List of players.
        :param active_pick: Active black card's pick count.
        :return: None
        :raises: GameHasEnded exception when the game cannot be played anymore.
        """
        min_cards_in_hand = min([len(player.cards_in_hand) for player in players])
        if min_cards_in_hand < active_pick + 1:
            raise GameHasEnded("Players ran out of cards!")

    def _elect_new_tzar(self):
        player = random.choice(
            [
                p
                for p in self.players
                if p.current_role != CardsAgainstHumanityRoles.TZAR
            ]
        )
        self.__revert_everyone_to_normal_player()
        player.elect_as_tzar()
        self.save()

    def __revert_everyone_to_normal_player(self):
        for p in self.players:
            p.revert_to_normal_player()

    def __finish_game(self, reason):
        self.state = GameStates.FINISHED
        raise GameHasEnded(reason)

    def save(self):
        os.makedirs("temp", exist_ok=True)
        with open(f"temp/{self.room_name}.jsonl", "a") as f:
            json.dump(self.dict(), f)
            f.write("\n")

    def load(self):
        pass

    def __hash__(self):
        return hash(str(self.dict()))


class GameStatePlayerView(BaseModel):
    player: CardsAgainstHumanityPlayer
    room_name: str
    state: str
    round_count: int
    currently_active_card: Optional[BlackCard] = None
    player_submissions: Dict[str, Submission] = Field(default_factory=dict)
    other_players: List[PlayerOutsideView]
    last_winners: Optional[List[LastWinnerInfo]]
    mode: str = GameModes.NORMAL

    @classmethod
    def from_game_state(cls, s: GameStateMachine, username: str):

        return cls(
            room_name=s.room_name,
            state=s.state,
            round_count=s.round_count,
            currently_active_card=s.currently_active_card,
            player_submissions=s.player_submissions,
            other_players=[PlayerOutsideView.from_player(p) for p in s.players],
            player=s.player_lookup[username],
            last_winners=s.last_winners,
            mode=s.mode,
        )

    def __hash__(self):
        return hash(str(self.dict()))
