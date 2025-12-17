"""
Simulated referee agent for league simulation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.game_rules import EvenOddGame
from league_sdk.helpers import generate_token
from .player import Player


class Referee:
    """Simulated referee agent."""

    def __init__(self, referee_id: str):
        self.referee_id = referee_id
        self.auth_token = generate_token()
        self.game = EvenOddGame()

    def conduct_match(self, player_a: Player, player_b: Player, match_id: str) -> dict:
        """Conduct a match between two players."""
        choice_a = player_a.choose_parity(player_b.player_id)
        choice_b = player_b.choose_parity(player_a.player_id)

        outcome = self.game.determine_match_outcome(
            player_a.player_id, choice_a,
            player_b.player_id, choice_b
        )

        player_a.record_result(outcome.player_a_result, player_b.player_id, choice_b)
        player_b.record_result(outcome.player_b_result, player_a.player_id, choice_a)

        return {
            "match_id": match_id,
            "player_a": player_a.player_id,
            "player_b": player_b.player_id,
            "choice_a": choice_a,
            "choice_b": choice_b,
            "drawn_number": outcome.drawn_number,
            "number_parity": outcome.number_parity,
            "result_a": outcome.player_a_result,
            "result_b": outcome.player_b_result,
            "winner": outcome.winner_id,
        }
