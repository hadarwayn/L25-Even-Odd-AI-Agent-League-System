"""
Base schema models and validators for the league protocol.
"""

import re
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class ParityChoice(str, Enum):
    """Valid parity choices."""
    EVEN = "even"
    ODD = "odd"


class GameResult(str, Enum):
    """Possible game results."""
    WIN = "WIN"
    LOSS = "LOSS"
    DRAW = "DRAW"
    TECHNICAL_LOSS = "TECHNICAL_LOSS"


class MatchRole(str, Enum):
    """Player role in a match."""
    PLAYER_A = "PLAYER_A"
    PLAYER_B = "PLAYER_B"


class AgentState(str, Enum):
    """Agent lifecycle states."""
    INIT = "INIT"
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    SHUTDOWN = "SHUTDOWN"


class ErrorCode(str, Enum):
    """Protocol error codes."""
    E001 = "E001"  # TIMEOUT_ERROR
    E003 = "E003"  # MISSING_REQUIRED_FIELD
    E004 = "E004"  # INVALID_PARITY_CHOICE
    E005 = "E005"  # PLAYER_NOT_REGISTERED
    E006 = "E006"  # REFEREE_NOT_REGISTERED
    E009 = "E009"  # CONNECTION_ERROR
    E011 = "E011"  # AUTH_TOKEN_MISSING
    E012 = "E012"  # AUTH_TOKEN_INVALID
    E018 = "E018"  # PROTOCOL_VERSION_MISMATCH
    E021 = "E021"  # INVALID_TIMESTAMP


def validate_utc_timestamp(v: str) -> str:
    """Validate UTC timestamp format."""
    z_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$"
    utc_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+00:00$"
    if not (re.match(z_pattern, v) or re.match(utc_pattern, v)):
        raise ValueError("Timestamp must be UTC (Z or +00:00)")
    return v


class MessageEnvelope(BaseModel):
    """Base message envelope for all protocol messages."""
    protocol: Literal["league.v2"] = "league.v2"
    message_type: str
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: Optional[str] = None

    @field_validator("timestamp")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        return validate_utc_timestamp(v)

    @field_validator("sender")
    @classmethod
    def validate_sender(cls, v: str) -> str:
        if ":" not in v:
            raise ValueError("Sender must be format 'type:id'")
        return v


class PlayerMeta(BaseModel):
    """Player metadata for registration."""
    display_name: str
    version: str = "1.0.0"
    protocol_version: str = "league.v2"
    game_types: list[str] = Field(default_factory=lambda: ["even_odd"])
    contact_endpoint: str


class RefereeMeta(BaseModel):
    """Referee metadata for registration."""
    version: str = "1.0.0"
    protocol_version: str = "league.v2"
    contact_endpoint: str


class StandingEntry(BaseModel):
    """Single entry in standings."""
    player_id: str
    display_name: Optional[str] = None
    points: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    played: int = 0
    rank: Optional[int] = None
