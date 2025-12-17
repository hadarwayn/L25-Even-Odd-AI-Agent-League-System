"""
Simulated player agent for league simulation.
"""

import random
import asyncio
from typing import Dict, List, Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.helpers import generate_token


class Player:
    """Simulated player agent with strategy."""

    def __init__(self, player_id: str, display_name: str, strategy: str):
        self.player_id = player_id
        self.display_name = display_name
        self.strategy = strategy
        self.auth_token = generate_token()
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.points = 0
        self.history: List[dict] = []
        self._last_choice = "even"
        self._opponent_history: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock() if asyncio else None

    def choose_parity(self, opponent_id: str) -> str:
        """Choose parity based on strategy."""
        if self.strategy == "random":
            return random.choice(["even", "odd"])
        elif self.strategy == "deterministic_even":
            return "even"
        elif self.strategy == "deterministic_odd":
            return "odd"
        elif self.strategy == "alternating":
            choice = self._last_choice
            self._last_choice = "odd" if choice == "even" else "even"
            return choice
        elif self.strategy == "adaptive":
            return self._adaptive_choice(opponent_id)
        return random.choice(["even", "odd"])

    def _adaptive_choice(self, opponent_id: str) -> str:
        """Make adaptive choice based on opponent history."""
        opp_hist = self._opponent_history.get(opponent_id, [])
        if len(opp_hist) < 2:
            return random.choice(["even", "odd"])
        even_count = opp_hist.count("even")
        odd_count = opp_hist.count("odd")
        return "even" if even_count >= odd_count else "odd"

    def record_result(self, result: str, opponent_id: str, opponent_choice: str):
        """Record match result."""
        if result == "WIN":
            self.wins += 1
            self.points += 3
        elif result == "DRAW":
            self.draws += 1
            self.points += 1
        else:
            self.losses += 1

        if opponent_id not in self._opponent_history:
            self._opponent_history[opponent_id] = []
        self._opponent_history[opponent_id].append(opponent_choice)
