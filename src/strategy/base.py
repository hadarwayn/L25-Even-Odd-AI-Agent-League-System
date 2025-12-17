"""
Base strategy interface for parity choice.

All strategies must implement the BaseStrategy abstract class.
"""

from abc import ABC, abstractmethod
from typing import Optional


class BaseStrategy(ABC):
    """
    Abstract base class for parity choice strategies.

    Implement choose_parity() to create a new strategy.
    """

    @abstractmethod
    def choose_parity(
        self,
        opponent_id: str,
        my_standings: dict,
        match_history: Optional[list] = None,
    ) -> str:
        """
        Choose 'even' or 'odd' for the current match.

        Args:
            opponent_id: ID of the opponent player
            my_standings: Current standings (wins, losses, draws)
            match_history: Optional list of past matches

        Returns:
            Either 'even' or 'odd'
        """
        pass

    def get_name(self) -> str:
        """Get the strategy name."""
        return self.__class__.__name__
