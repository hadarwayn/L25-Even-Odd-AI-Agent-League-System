"""
Helper utilities for the league system.

Provides UTC timestamps, ID generation, and validation functions.
"""

import re
import uuid
import secrets
from datetime import datetime, timezone
from typing import Optional


def utc_now() -> str:
    """Generate current UTC timestamp with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def generate_token(length: int = 32) -> str:
    """Generate a secure random token."""
    return secrets.token_hex(length // 2)


def validate_utc(timestamp: str) -> bool:
    """
    Validate that a timestamp is in UTC format.

    Valid formats:
    - 2025-01-15T10:30:00Z
    - 2025-01-15T10:30:00+00:00

    Invalid formats:
    - 2025-01-15T10:30:00+02:00 (non-UTC timezone)
    - 2025-01-15T10:30:00 (no timezone)
    """
    if not timestamp:
        return False

    # Pattern for Z suffix
    z_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    # Pattern for +00:00 suffix
    utc_offset_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$"

    return bool(re.match(z_pattern, timestamp) or re.match(utc_offset_pattern, timestamp))


def parse_sender(sender: str) -> tuple[str, str]:
    """
    Parse sender string into type and ID.

    Args:
        sender: Format "type:id" (e.g., "player:P01")

    Returns:
        Tuple of (type, id)
    """
    if ":" not in sender:
        raise ValueError(f"Invalid sender format: {sender}")
    parts = sender.split(":", 1)
    return parts[0], parts[1]


def format_sender(agent_type: str, agent_id: str) -> str:
    """
    Format agent type and ID into sender string.

    Args:
        agent_type: Type of agent (player, referee, manager)
        agent_id: Agent identifier

    Returns:
        Formatted sender string (e.g., "player:P01")
    """
    return f"{agent_type}:{agent_id}"


def is_retryable_error(error_code: str) -> bool:
    """Check if an error code is retryable."""
    return error_code in ("E001", "E009")


def calculate_points(result: str) -> int:
    """
    Calculate points for a match result.

    Args:
        result: WIN, DRAW, LOSS, or TECHNICAL_LOSS

    Returns:
        Points (Win=3, Draw=1, Loss=0)
    """
    points_map = {
        "WIN": 3,
        "DRAW": 1,
        "LOSS": 0,
        "TECHNICAL_LOSS": 0,
    }
    return points_map.get(result, 0)


def determine_parity(number: int) -> str:
    """Determine if a number is even or odd."""
    return "even" if number % 2 == 0 else "odd"
