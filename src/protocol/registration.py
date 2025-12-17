"""
Registration message models for league.v2 protocol.

Handles LEAGUE_REGISTER_REQUEST and LEAGUE_REGISTER_RESPONSE messages.
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from .envelope import MessageEnvelope, create_envelope, get_utc_timestamp


class RegistrationStatus(str, Enum):
    """Registration response status."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class PlayerMeta(BaseModel):
    """
    Metadata about the player agent.

    Sent during registration to describe the agent's capabilities.
    """

    display_name: str
    version: str
    protocol_version: str = "2.1.0"
    game_types: list[str] = Field(default=["even_odd"])
    contact_endpoint: str


class LeagueRegisterRequest(BaseModel):
    """
    LEAGUE_REGISTER_REQUEST message.

    Sent by player to League Manager to join the league.
    """

    protocol: str = "league.v2"
    message_type: str = "LEAGUE_REGISTER_REQUEST"
    sender: str = "player:UNREGISTERED"
    timestamp: str
    conversation_id: str
    player_meta: PlayerMeta


class LeagueRegisterResponse(BaseModel):
    """
    LEAGUE_REGISTER_RESPONSE message.

    Sent by League Manager after processing registration request.
    Contains player_id and auth_token if accepted.
    """

    protocol: str = "league.v2"
    message_type: str = "LEAGUE_REGISTER_RESPONSE"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    status: RegistrationStatus
    player_id: Optional[str] = None
    auth_token: Optional[str] = None
    league_id: Optional[str] = None
    reason: Optional[str] = None


def create_register_request(
    display_name: str,
    contact_endpoint: str,
    version: str = "1.0.0",
    protocol_version: str = "2.1.0",
    game_types: Optional[list[str]] = None,
    conversation_id: Optional[str] = None,
) -> dict:
    """
    Create a LEAGUE_REGISTER_REQUEST message.

    Args:
        display_name: Name to display for this agent
        contact_endpoint: URL where agent receives messages
        version: Agent software version
        protocol_version: Protocol version supported
        game_types: List of game types agent can play
        conversation_id: Optional conversation ID

    Returns:
        Dictionary representation of the request message
    """
    envelope = create_envelope(
        message_type="LEAGUE_REGISTER_REQUEST",
        sender="player:UNREGISTERED",
        conversation_id=conversation_id,
    )

    player_meta = PlayerMeta(
        display_name=display_name,
        version=version,
        protocol_version=protocol_version,
        game_types=game_types or ["even_odd"],
        contact_endpoint=contact_endpoint,
    )

    request = LeagueRegisterRequest(
        timestamp=envelope.timestamp,
        conversation_id=envelope.conversation_id,
        player_meta=player_meta,
    )

    return request.model_dump()


def parse_register_response(data: dict) -> LeagueRegisterResponse:
    """
    Parse a LEAGUE_REGISTER_RESPONSE message.

    Args:
        data: Dictionary from JSON response

    Returns:
        Parsed LeagueRegisterResponse object

    Raises:
        ValidationError: If response doesn't match expected schema
    """
    return LeagueRegisterResponse.model_validate(data)
