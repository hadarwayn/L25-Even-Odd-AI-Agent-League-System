"""
Simulation package for Even/Odd League.

Provides simulation components for running league games.
"""

from .player import Player
from .referee import Referee
from .league import LeagueSimulation
from .output import (
    print_standings,
    print_match_history,
    print_activity_log,
    print_final_results,
)

__all__ = [
    "Player",
    "Referee",
    "LeagueSimulation",
    "print_standings",
    "print_match_history",
    "print_activity_log",
    "print_final_results",
]
