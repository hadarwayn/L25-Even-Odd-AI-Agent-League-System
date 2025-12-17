"""
Random strategy - equal probability even/odd.
"""

import random
from typing import Optional, Literal

from .base import BaseStrategy, ParityChoice


class RandomStrategy(BaseStrategy):
    """Random parity choice strategy."""

    @property
    def name(self) -> str:
        return "RandomStrategy"

    def choose(
        self,
        match_id: str,
        opponent_id: str,
        history: Optional[list[dict]] = None,
    ) -> ParityChoice:
        """Choose randomly between even and odd."""
        return random.choice(["even", "odd"])
