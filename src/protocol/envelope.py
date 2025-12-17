"""
Message Envelope for league.v2 protocol.

All messages must include the envelope fields for proper routing and tracking.
Timestamps must be in UTC (with Z suffix or +00:00).
"""

from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import uuid


class MessageEnvelope(BaseModel):
    """
    Base envelope for all league.v2 protocol messages.

    Required fields:
    - protocol: Always "league.v2"
    - message_type: Type of message (e.g., GAME_INVITATION)
    - sender: Format "type:id" (e.g., player:P01, referee:REF01)
    - timestamp: UTC ISO-8601 with Z suffix
    - conversation_id: Unique ID for message thread tracking

    Optional fields (context-dependent):
    - auth_token: Required after registration
    - league_id, round_id, match_id: Game context
    """

    protocol: str = Field(default="league.v2", frozen=True)
    message_type: str
    sender: str
    timestamp: str
    conversation_id: str

    # Optional fields
    auth_token: Optional[str] = None
    league_id: Optional[str] = None
    round_id: Optional[int] = None
    match_id: Optional[str] = None

    @field_validator("timestamp")
    @classmethod
    def validate_utc_timestamp(cls, v: str) -> str:
        """
        Validate that timestamp is in UTC format.

        Valid formats:
        - 2025-01-15T10:30:00Z (Z suffix)
        - 2025-01-15T10:30:00+00:00 (+00:00 offset)

        Invalid:
        - 2025-01-15T10:30:00+02:00 (non-UTC offset)
        - 2025-01-15T10:30:00 (no timezone)
        """
        if not v.endswith("Z") and not v.endswith("+00:00"):
            raise ValueError(
                f"Timestamp must be UTC (end with Z or +00:00), got: {v}"
            )

        # Validate it parses correctly
        try:
            if v.endswith("Z"):
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            else:
                datetime.fromisoformat(v)
        except ValueError as e:
            raise ValueError(f"Invalid ISO-8601 timestamp: {v}") from e

        return v

    @field_validator("sender")
    @classmethod
    def validate_sender_format(cls, v: str) -> str:
        """
        Validate sender format is type:id or league_manager.

        Valid formats:
        - player:P01
        - player:UNREGISTERED
        - referee:REF01
        - league_manager
        """
        if v == "league_manager":
            return v

        if ":" not in v:
            raise ValueError(
                f"Sender must be 'type:id' format or 'league_manager', got: {v}"
            )

        sender_type, sender_id = v.split(":", 1)
        valid_types = {"player", "referee"}

        if sender_type not in valid_types:
            raise ValueError(
                f"Sender type must be one of {valid_types}, got: {sender_type}"
            )

        return v


def get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO-8601 format with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_conversation_id(prefix: str = "conv") -> str:
    """Generate a unique conversation ID."""
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def create_envelope(
    message_type: str,
    sender: str,
    conversation_id: Optional[str] = None,
    auth_token: Optional[str] = None,
    league_id: Optional[str] = None,
    round_id: Optional[int] = None,
    match_id: Optional[str] = None,
) -> MessageEnvelope:
    """
    Create a message envelope with current timestamp.

    Args:
        message_type: Type of message (e.g., GAME_JOIN_ACK)
        sender: Sender in format type:id (e.g., player:P01)
        conversation_id: Optional conversation ID (generated if not provided)
        auth_token: Authentication token (required after registration)
        league_id: League identifier
        round_id: Round number
        match_id: Match identifier

    Returns:
        MessageEnvelope with all required fields populated
    """
    return MessageEnvelope(
        message_type=message_type,
        sender=sender,
        timestamp=get_utc_timestamp(),
        conversation_id=conversation_id or generate_conversation_id(),
        auth_token=auth_token,
        league_id=league_id,
        round_id=round_id,
        match_id=match_id,
    )
