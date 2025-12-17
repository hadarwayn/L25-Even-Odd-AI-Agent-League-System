"""
Base strategy interface for player agents.
"""

from abc import ABC, abstractmethod
from typing import Literal, Optional


ParityChoice = Literal["even", "odd"]


class BaseStrategy(ABC):
    """Abstract base class for parity choice strategies."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name."""
        pass

    @abstractmethod
    def choose(
        self,
        match_id: str,
        opponent_id: str,
        history: Optional[list[dict]] = None,
    ) -> ParityChoice:
        """
        Choose parity for a match.

        Args:
            match_id: Current match identifier
            opponent_id: Opponent's player ID
            history: Optional game history for adaptive strategies

        Returns:
            "even" or "odd"
        """
        pass

    def update(self, result: dict) -> None:
        """
        Update strategy state after a match.

        Args:
            result: Match result including choice and outcome
        """
        pass
