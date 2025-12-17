"""
Referee agent template package.

The Referee is responsible for:
- Match orchestration between two players
- Collecting parity choices
- Determining winners based on random number
- Reporting results to League Manager
"""

from .handlers import RefereeHandlers
from .game_logic import MatchOrchestrator

__all__ = [
    "RefereeHandlers",
    "MatchOrchestrator",
]
