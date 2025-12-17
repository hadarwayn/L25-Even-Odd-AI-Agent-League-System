"""
Error models and codes for league.v2 protocol.

Defines LEAGUE_ERROR and GAME_ERROR message types along with
the standard error codes used throughout the protocol.
"""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel


class ErrorCode(str, Enum):
    """
    Standard error codes for the league.v2 protocol.

    Retryable errors (E001, E009) can be attempted again.
    Other errors indicate permanent failures.
    """

    # Retryable errors
    TIMEOUT_ERROR = "E001"
    CONNECTION_ERROR = "E009"

    # Validation errors
    MISSING_REQUIRED_FIELD = "E003"
    INVALID_PARITY_CHOICE = "E004"

    # Registration errors
    PLAYER_NOT_REGISTERED = "E005"

    # Authentication errors
    AUTH_TOKEN_MISSING = "E011"
    AUTH_TOKEN_INVALID = "E012"

    # Protocol errors
    PROTOCOL_VERSION_MISMATCH = "E018"
    INVALID_TIMESTAMP = "E021"


# Map error codes to whether they are retryable
RETRYABLE_ERRORS = {ErrorCode.TIMEOUT_ERROR, ErrorCode.CONNECTION_ERROR}


def is_retryable(error_code: str) -> bool:
    """Check if an error code indicates a retryable error."""
    try:
        code = ErrorCode(error_code)
        return code in RETRYABLE_ERRORS
    except ValueError:
        return False


class LeagueError(BaseModel):
    """
    LEAGUE_ERROR message from League Manager.

    Sent when a league-level error occurs (e.g., player not registered).
    """

    protocol: str = "league.v2"
    message_type: str = "LEAGUE_ERROR"
    sender: str = "league_manager"
    timestamp: str

    error_code: str
    error_name: str
    error_description: str
    context: Optional[dict[str, Any]] = None
    retryable: bool = False


class GameError(BaseModel):
    """
    GAME_ERROR message from Referee.

    Sent when a game-level error occurs (e.g., timeout during choice).
    """

    protocol: str = "league.v2"
    message_type: str = "GAME_ERROR"
    sender: str
    timestamp: str

    match_id: str
    player_id: str
    error_code: str
    error_name: str
    error_description: str
    game_state: Optional[str] = None
    retryable: bool = False
    retry_count: int = 0
    max_retries: int = 3


def create_error_context(error_code: ErrorCode, **kwargs) -> dict[str, Any]:
    """
    Create an error context dictionary.

    Args:
        error_code: The error code
        **kwargs: Additional context fields

    Returns:
        Dictionary with error details
    """
    error_info = {
        ErrorCode.TIMEOUT_ERROR: {
            "name": "TIMEOUT_ERROR",
            "description": "Response not received in time",
        },
        ErrorCode.CONNECTION_ERROR: {
            "name": "CONNECTION_ERROR",
            "description": "Connection failure",
        },
        ErrorCode.MISSING_REQUIRED_FIELD: {
            "name": "MISSING_REQUIRED_FIELD",
            "description": "Required field missing",
        },
        ErrorCode.INVALID_PARITY_CHOICE: {
            "name": "INVALID_PARITY_CHOICE",
            "description": "Invalid choice (not 'even' or 'odd')",
        },
        ErrorCode.PLAYER_NOT_REGISTERED: {
            "name": "PLAYER_NOT_REGISTERED",
            "description": "Player ID not found in registry",
        },
        ErrorCode.AUTH_TOKEN_MISSING: {
            "name": "AUTH_TOKEN_MISSING",
            "description": "Auth token not included",
        },
        ErrorCode.AUTH_TOKEN_INVALID: {
            "name": "AUTH_TOKEN_INVALID",
            "description": "Auth token is invalid",
        },
        ErrorCode.PROTOCOL_VERSION_MISMATCH: {
            "name": "PROTOCOL_VERSION_MISMATCH",
            "description": "Protocol version incompatible",
        },
        ErrorCode.INVALID_TIMESTAMP: {
            "name": "INVALID_TIMESTAMP",
            "description": "Timestamp not in UTC format",
        },
    }

    info = error_info.get(error_code, {"name": "UNKNOWN", "description": "Unknown error"})

    return {
        "error_code": error_code.value,
        "error_name": info["name"],
        "error_description": info["description"],
        "retryable": is_retryable(error_code.value),
        **kwargs,
    }
