from collections import Counter
from typing import Optional, Dict

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

    def player_select_winner(self, username: str, awarded: SelectWinningSubmission):
        self.winner_votes[username] = awarded

        if len(self.winner_votes.keys()) == len(self.players):
            vote_counter = Counter(list(self.winner_votes.values()))
            submission, _ = vote_counter.most_common(1)[0]
            self.select_winner(submission)
            self.winner_votes = {}

    def tzar(self) -> Optional[CardsAgainstHumanityPlayer]:
        return None

    def _elect_new_tzar(self):
        pass
