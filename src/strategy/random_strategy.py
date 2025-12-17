"""
Random strategy for parity choice.

Simple strategy that chooses 'even' or 'odd' with equal probability.
"""

import random
from typing import Optional

from .base import BaseStrategy


class RandomStrategy(BaseStrategy):
    """
    Random parity choice strategy.

    Chooses 'even' or 'odd' with 50/50 probability.
    This is a baseline strategy for testing and comparison.
    """

    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the random strategy.

        Args:
            seed: Optional random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)

    def choose_parity(
        self,
        opponent_id: str,
        my_standings: dict,
        match_history: Optional[list] = None,
    ) -> str:
        """
        Choose 'even' or 'odd' randomly.

        Args:
            opponent_id: ID of opponent (ignored in random strategy)
            my_standings: Current standings (ignored in random strategy)
            match_history: Past matches (ignored in random strategy)

        Returns:
            Either 'even' or 'odd' with equal probability
        """
        return random.choice(["even", "odd"])
