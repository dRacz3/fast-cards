from collections import Counter
from typing import Optional, Dict, List, Tuple

from src.internal.cards_against_humanity_rules.game_related_exceptions import (
    InvalidPlayerAction,
)
from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStateMachine,
)
from src.internal.cards_against_humanity_rules.models import (
    SelectWinningSubmission,
    CardsAgainstHumanityPlayer,
    GameModes,
    GameStates,
)


class GodIsDeadModeStateMachine(GameStateMachine):
    winner_votes: Dict[str, SelectWinningSubmission] = {}
    mode: str = GameModes.GOD_IS_DEAD

    def select_winner(self, sender_name: str, winner: SelectWinningSubmission):
        self.winner_votes[sender_name] = winner
        self.player_lookup[sender_name].votes = [winner]

        if len(self.winner_votes.keys()) == len(self.players):
            winner_counter: Dict[SelectWinningSubmission, int] = {}
            for vote in self.winner_votes.values():
                if vote in winner_counter:
                    winner_counter[vote] += 1
                else:
                    winner_counter[vote] = 1

            max_vote_count = max(list(winner_counter.values()))
            winners: List[Tuple[SelectWinningSubmission, int]] = [
                c for c in winner_counter.items() if c[1] == max_vote_count
            ]
            winning_subbmissions = [s[0] for s in winners]
            self._select_winner(winning_subbmissions)

    def tzar(self) -> Optional[CardsAgainstHumanityPlayer]:
        return None

    def _elect_new_tzar(self):
        pass

    def _advance(self):
        if len(self.player_submissions.keys()) == len(self.players):
            self._close_round()

    def advance_after_voting(self):
        if self.state == GameStates.TZAR_CHOOSING_WINNER:
            if len(self.winner_votes.keys()) == len(self.players):
                self.winner_votes = {}
                for players in self.player_lookup.values():
                    players.votes = []
                self._start_new_round()
            else:
                raise InvalidPlayerAction("Cannot advance if not everyone has voted!")
        else:
            raise InvalidPlayerAction(
                f"Cannot advance using this step unless in state: {GameStates.TZAR_CHOOSING_WINNER}"
            )
