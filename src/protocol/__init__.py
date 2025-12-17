"""
Protocol package.

Contains Pydantic models for the league.v2 protocol messages.
All messages follow JSON-RPC 2.0 over HTTP transport.
"""

from .envelope import MessageEnvelope, create_envelope, get_utc_timestamp
from .errors import ErrorCode, LeagueError, GameError

__all__ = [
    "MessageEnvelope",
    "create_envelope",
    "get_utc_timestamp",
    "ErrorCode",
    "LeagueError",
    "GameError",
]
