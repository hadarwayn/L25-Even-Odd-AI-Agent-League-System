"""
Alternating strategy - switches between even and odd each game.
"""

from typing import Optional

from .base import BaseStrategy, ParityChoice


class AlternatingStrategy(BaseStrategy):
    """Alternates between even and odd each game."""

    def __init__(self, start_with: ParityChoice = "even"):
        """
        Initialize alternating strategy.

        Args:
            start_with: First choice ("even" or "odd")
        """
        self._current: ParityChoice = start_with
        self._game_count = 0

    @property
    def name(self) -> str:
        return "AlternatingStrategy"

    def choose(
        self,
        match_id: str,
        opponent_id: str,
        history: Optional[list[dict]] = None,
    ) -> ParityChoice:
        """Alternate between even and odd."""
        choice = self._current
        return choice

    def update(self, result: dict) -> None:
        """Switch to opposite choice after each game."""
        self._game_count += 1
        self._current = "odd" if self._current == "even" else "even"
