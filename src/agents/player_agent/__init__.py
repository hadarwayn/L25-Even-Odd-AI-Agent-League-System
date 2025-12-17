"""
Player Agent package.

Implements a Player Agent that:
- Registers with the League Manager
- Accepts game invitations
- Makes parity choices using a strategy
- Processes game results
"""

from .state import PlayerState, AgentLifecycle
from .server import create_app

__all__ = ["PlayerState", "AgentLifecycle", "create_app"]
