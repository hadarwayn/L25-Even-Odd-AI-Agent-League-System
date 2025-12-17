"""
Deterministic strategies - always choose the same option.
"""

from typing import Optional

from .base import BaseStrategy, ParityChoice


class DeterministicEvenStrategy(BaseStrategy):
    """Always choose even."""

    @property
    def name(self) -> str:
        return "DeterministicEven"

    def choose(
        self,
        match_id: str,
        opponent_id: str,
        history: Optional[list[dict]] = None,
    ) -> ParityChoice:
        """Always return even."""
        return "even"


class DeterministicOddStrategy(BaseStrategy):
    """Always choose odd."""

    @property
    def name(self) -> str:
        return "DeterministicOdd"

    def choose(
        self,
        match_id: str,
        opponent_id: str,
        history: Optional[list[dict]] = None,
    ) -> ParityChoice:
        """Always return odd."""
        return "odd"
