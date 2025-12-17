"""
League Manager agent package.

The League Manager is the orchestrator responsible for:
- Player and referee registration
- Round-robin schedule generation
- Standings calculation and broadcasting
- League lifecycle management
"""

from .handlers import LeagueManagerHandlers
from .scheduler import LeagueScheduler
from .standings import StandingsManager

__all__ = [
    "LeagueManagerHandlers",
    "LeagueScheduler",
    "StandingsManager",
]
