from collections import Counter
from typing import Optional, Dict, List, Tuple

from src.internal.cards_against_humanity_rules.game_state_machine import (
    GameStateMachine,
)
from src.internal.cards_against_humanity_rules.models import (
    SelectWinningSubmission,
    CardsAgainstHumanityPlayer,
    GameModes,
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
                if vote in winner_counter.keys():
                    winner_counter[vote] += 1
                else:
                    winner_counter[vote] = 1

            max_vote_count = max(list(winner_counter.values()))
            winners: List[Tuple[SelectWinningSubmission, int]] = list(
                filter(lambda v: v[1] == max_vote_count, winner_counter.items())
            )
            winning_subbmissions = [s[0] for s in winners]
            self._select_winner(winning_subbmissions)
            self.winner_votes = {}
            self.player_lookup[sender_name].votes = []

    def tzar(self) -> Optional[CardsAgainstHumanityPlayer]:
        return None

    def _elect_new_tzar(self):
        pass

    def _advance(self):
        if len(self.player_submissions.keys()) == len(self.players):
            self._close_round()
