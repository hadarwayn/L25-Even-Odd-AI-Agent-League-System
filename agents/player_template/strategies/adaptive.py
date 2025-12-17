"""
Adaptive strategy - learns from opponent history.
"""

from typing import Optional
from collections import defaultdict
import random

from .base import BaseStrategy, ParityChoice


class AdaptiveStrategy(BaseStrategy):
    """
    Adapts to opponent behavior based on game history.

    Tracks opponent's choice patterns and counters accordingly.
    """

    def __init__(self):
        """Initialize adaptive strategy."""
        # Track opponent choices: opponent_id -> list of choices
        self._opponent_history: dict[str, list[ParityChoice]] = defaultdict(list)

    @property
    def name(self) -> str:
        return "AdaptiveStrategy"

    def choose(
        self,
        match_id: str,
        opponent_id: str,
        history: Optional[list[dict]] = None,
    ) -> ParityChoice:
        """
        Choose based on opponent's historical preferences.

        Strategy:
        - If opponent tends to choose even, we choose even (hoping for draw or win)
        - If opponent tends to choose odd, we choose odd
        - With insufficient data, choose randomly
        """
        opponent_choices = self._opponent_history.get(opponent_id, [])

        if len(opponent_choices) < 3:
            # Not enough data, choose randomly
            return random.choice(["even", "odd"])

        # Count opponent's choices
        even_count = opponent_choices.count("even")
        odd_count = opponent_choices.count("odd")

        # Mirror opponent's preference (increases chance of draw or win)
        if even_count > odd_count:
            return "even"
        elif odd_count > even_count:
            return "odd"
        else:
            return random.choice(["even", "odd"])

    def update(self, result: dict) -> None:
        """Record opponent's choice for future analysis."""
        opponent_id = result.get("opponent_id")
        opponent_choice = result.get("opponent_choice")

        if opponent_id and opponent_choice:
            self._opponent_history[opponent_id].append(opponent_choice)
            # Keep only last 10 choices
            if len(self._opponent_history[opponent_id]) > 10:
                self._opponent_history[opponent_id] = self._opponent_history[opponent_id][-10:]
