"""
Even/Odd game logic.

Implements the rules for determining winners in Even/Odd games.
"""

import random
from typing import Literal, Optional
from dataclasses import dataclass


ParityChoice = Literal["even", "odd"]
GameResult = Literal["WIN", "LOSS", "DRAW", "TECHNICAL_LOSS"]


@dataclass
class MatchOutcome:
    """Result of a match."""
    drawn_number: int
    number_parity: ParityChoice
    player_a_choice: ParityChoice
    player_b_choice: ParityChoice
    player_a_result: GameResult
    player_b_result: GameResult
    winner_id: Optional[str]


class EvenOddGame:
    """Even/Odd game logic handler."""

    def __init__(self, min_number: int = 1, max_number: int = 10):
        """
        Initialize game.

        Args:
            min_number: Minimum number in range (inclusive)
            max_number: Maximum number in range (inclusive)
        """
        self.min_number = min_number
        self.max_number = max_number

    def draw_number(self) -> int:
        """Draw a random number."""
        return random.randint(self.min_number, self.max_number)

    def get_parity(self, number: int) -> ParityChoice:
        """Determine if number is even or odd."""
        return "even" if number % 2 == 0 else "odd"

    def determine_match_outcome(
        self,
        player_a_id: str,
        player_a_choice: ParityChoice,
        player_b_id: str,
        player_b_choice: ParityChoice,
        drawn_number: Optional[int] = None,
    ) -> MatchOutcome:
        """
        Determine the outcome of a match.

        Args:
            player_a_id: Player A identifier
            player_a_choice: Player A's parity choice
            player_b_id: Player B identifier
            player_b_choice: Player B's parity choice
            drawn_number: Pre-drawn number (optional, for testing)

        Returns:
            MatchOutcome with results for both players
        """
        if drawn_number is None:
            drawn_number = self.draw_number()

        number_parity = self.get_parity(drawn_number)

        a_correct = player_a_choice == number_parity
        b_correct = player_b_choice == number_parity

        if a_correct and b_correct:
            # Both correct - draw
            player_a_result = "DRAW"
            player_b_result = "DRAW"
            winner_id = None
        elif a_correct:
            # A wins
            player_a_result = "WIN"
            player_b_result = "LOSS"
            winner_id = player_a_id
        elif b_correct:
            # B wins
            player_a_result = "LOSS"
            player_b_result = "WIN"
            winner_id = player_b_id
        else:
            # Neither correct - draw
            player_a_result = "DRAW"
            player_b_result = "DRAW"
            winner_id = None

        return MatchOutcome(
            drawn_number=drawn_number,
            number_parity=number_parity,
            player_a_choice=player_a_choice,
            player_b_choice=player_b_choice,
            player_a_result=player_a_result,
            player_b_result=player_b_result,
            winner_id=winner_id,
        )


def determine_winner(
    player_a_choice: ParityChoice,
    player_b_choice: ParityChoice,
    drawn_number: int,
) -> tuple[GameResult, GameResult, Optional[str]]:
    """
    Convenience function to determine winner.

    Returns:
        Tuple of (player_a_result, player_b_result, winner_id or None)
    """
    game = EvenOddGame()
    outcome = game.determine_match_outcome(
        "A", player_a_choice, "B", player_b_choice, drawn_number
    )
    winner = None
    if outcome.winner_id == "A":
        winner = "player_a"
    elif outcome.winner_id == "B":
        winner = "player_b"
    return outcome.player_a_result, outcome.player_b_result, winner
