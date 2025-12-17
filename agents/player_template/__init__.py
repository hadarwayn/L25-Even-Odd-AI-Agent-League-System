"""
Player agent template package.

The Player agent is responsible for:
- Registering with the League Manager
- Accepting game invitations
- Making parity choices using strategies
- Processing game results
"""

from .handlers import PlayerHandlers
from .state import PlayerState

__all__ = [
    "PlayerHandlers",
    "PlayerState",
]
