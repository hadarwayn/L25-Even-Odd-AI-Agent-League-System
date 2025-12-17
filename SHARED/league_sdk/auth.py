"""
Authentication and rate limiting utilities.

Provides token validation, rate limiting, and security helpers.
"""

import html
import time
from collections import defaultdict
from typing import Optional, Dict, Set
from dataclasses import dataclass, field


# Named constants for configuration
DEFAULT_RATE_LIMIT = 100  # Max requests per window
RATE_LIMIT_WINDOW_SECONDS = 60  # Window duration in seconds
MAX_DISPLAY_NAME_LENGTH = 50  # Maximum display name length
TOKEN_MIN_LENGTH = 16  # Minimum valid token length


@dataclass
class RateLimiter:
    """
    Rate limiter using sliding window algorithm.

    Limits requests per sender to prevent abuse.
    """
    max_requests: int = DEFAULT_RATE_LIMIT
    window_seconds: int = RATE_LIMIT_WINDOW_SECONDS
    _requests: Dict[str, list] = field(default_factory=lambda: defaultdict(list))

    def is_allowed(self, sender: str) -> bool:
        """
        Check if a request from sender is allowed.

        Args:
            sender: Identifier of the requester

        Returns:
            True if request is allowed, False if rate limited
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        self._requests[sender] = [
            t for t in self._requests[sender] if t > window_start
        ]

        # Check limit
        if len(self._requests[sender]) >= self.max_requests:
            return False

        # Record this request
        self._requests[sender].append(now)
        return True

    def get_remaining(self, sender: str) -> int:
        """Get remaining requests for sender in current window."""
        now = time.time()
        window_start = now - self.window_seconds

        current_count = sum(
            1 for t in self._requests.get(sender, []) if t > window_start
        )
        return max(0, self.max_requests - current_count)


class AuthTokenValidator:
    """
    Token validator for authenticated requests.

    Validates auth_tokens against registered tokens.
    """

    def __init__(self):
        self._valid_tokens: Dict[str, str] = {}  # token -> agent_id
        self._agent_tokens: Dict[str, str] = {}  # agent_id -> token

    def register_token(self, agent_id: str, token: str) -> None:
        """Register a valid token for an agent."""
        self._valid_tokens[token] = agent_id
        self._agent_tokens[agent_id] = token

    def unregister_token(self, agent_id: str) -> None:
        """Unregister an agent's token."""
        token = self._agent_tokens.pop(agent_id, None)
        if token:
            self._valid_tokens.pop(token, None)

    def validate_token(
        self,
        token: Optional[str],
        expected_agent_id: Optional[str] = None
    ) -> bool:
        """
        Validate an auth token.

        Args:
            token: The token to validate
            expected_agent_id: If provided, verify token belongs to this agent

        Returns:
            True if token is valid
        """
        if not token or len(token) < TOKEN_MIN_LENGTH:
            return False

        if token not in self._valid_tokens:
            return False

        if expected_agent_id:
            return self._valid_tokens[token] == expected_agent_id

        return True

    def get_agent_for_token(self, token: str) -> Optional[str]:
        """Get the agent ID associated with a token."""
        return self._valid_tokens.get(token)


def sanitize_display_name(name: str) -> str:
    """
    Sanitize display name for safe storage and display.

    - Escapes HTML entities to prevent XSS
    - Limits length to MAX_DISPLAY_NAME_LENGTH
    - Strips leading/trailing whitespace

    Args:
        name: Raw display name

    Returns:
        Sanitized display name
    """
    if not name:
        return ""

    sanitized = html.escape(name.strip())
    return sanitized[:MAX_DISPLAY_NAME_LENGTH]


def sanitize_metadata(metadata: dict) -> dict:
    """
    Sanitize all string values in metadata dictionary.

    Args:
        metadata: Raw metadata dictionary

    Returns:
        Sanitized metadata dictionary
    """
    sanitized = {}
    for key, value in metadata.items():
        if isinstance(value, str):
            sanitized[key] = html.escape(value)[:200]
        elif isinstance(value, dict):
            sanitized[key] = sanitize_metadata(value)
        elif isinstance(value, list):
            sanitized[key] = [
                html.escape(v)[:200] if isinstance(v, str) else v
                for v in value
            ]
        else:
            sanitized[key] = value
    return sanitized


# Message types that require authentication
AUTH_REQUIRED_MESSAGE_TYPES: Set[str] = {
    "GAME_JOIN_ACK",
    "CHOOSE_PARITY_RESPONSE",
    "QUERY_STANDINGS_REQUEST",
    "QUERY_SCHEDULE_REQUEST",
    "LEAGUE_UNREGISTER_REQUEST",
    "REPORT_MATCH_RESULT",
    "CHOOSE_PARITY_CALL",
    "GAME_INVITATION",
    "GAME_OVER",
}


def requires_auth(message_type: str) -> bool:
    """Check if a message type requires authentication."""
    return message_type in AUTH_REQUIRED_MESSAGE_TYPES
