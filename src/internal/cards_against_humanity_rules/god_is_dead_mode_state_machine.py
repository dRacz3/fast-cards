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

        if len(self.winner_votes.keys()):
            vote_counter = Counter(self.winner_votes.values())
            _, submission = vote_counter.most_common(1)
            self.select_winner(SelectWinningSubmission(submission=submission))
            self.winner_votes = {}

    def tzar(self) -> Optional[CardsAgainstHumanityPlayer]:
        return None

    def __elect_new_tzar(self):
        print("[__elect_new_tzar] Using subclass")
        self.save()
