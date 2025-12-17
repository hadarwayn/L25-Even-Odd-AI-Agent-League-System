"""
Game message models for league.v2 protocol.

Handles the match flow messages:
- GAME_INVITATION
- GAME_JOIN_ACK
- CHOOSE_PARITY_CALL
- CHOOSE_PARITY_RESPONSE
- GAME_OVER
- LEAGUE_STANDINGS_UPDATE
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class ParityChoice(str, Enum):
    """Valid parity choices for Even/Odd game."""

    EVEN = "even"
    ODD = "odd"


class RoleInMatch(str, Enum):
    """Player role in a match."""

    PLAYER_A = "PLAYER_A"
    PLAYER_B = "PLAYER_B"


class GameResultStatus(str, Enum):
    """Possible game result statuses."""

    WIN = "WIN"
    DRAW = "DRAW"
    TECHNICAL_LOSS = "TECHNICAL_LOSS"


# --- Game Invitation ---
class GameInvitationDetails(BaseModel):
    """Details within a GAME_INVITATION message."""

    game_type: str = "even_odd"
    match_id: str
    role_in_match: RoleInMatch
    opponent_id: str


class GameInvitation(BaseModel):
    """GAME_INVITATION message from Referee to Player."""

    protocol: str = "league.v2"
    message_type: str = "GAME_INVITATION"
    sender: str
    timestamp: str
    conversation_id: str
    league_id: str
    round_id: int
    match_id: str
    game_invitation: GameInvitationDetails


# --- Game Join Acknowledgment ---
class GameJoinAck(BaseModel):
    """GAME_JOIN_ACK message from Player to Referee."""

    protocol: str = "league.v2"
    message_type: str = "GAME_JOIN_ACK"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str
    league_id: str
    round_id: int
    match_id: str
    accept: bool = True


# --- Choose Parity Call ---
class ParityContext(BaseModel):
    """Context provided for making parity choice."""

    valid_options: list[str] = Field(default=["even", "odd"])
    your_standings: dict = Field(default_factory=lambda: {"wins": 0, "losses": 0, "draws": 0})
    opponent_id: str


class ChooseParityCall(BaseModel):
    """CHOOSE_PARITY_CALL message from Referee to Player."""

    protocol: str = "league.v2"
    message_type: str = "CHOOSE_PARITY_CALL"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: Optional[str] = None
    league_id: str
    round_id: int
    match_id: str
    player_id: str
    parity_context: ParityContext
    deadline: str


# --- Choose Parity Response ---
class ChooseParityResponse(BaseModel):
    """CHOOSE_PARITY_RESPONSE message from Player to Referee."""

    protocol: str = "league.v2"
    message_type: str = "CHOOSE_PARITY_RESPONSE"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str
    league_id: str
    round_id: int
    match_id: str
    player_id: str
    parity_choice: ParityChoice

    @field_validator("parity_choice", mode="before")
    @classmethod
    def validate_parity(cls, v):
        """Ensure parity choice is valid."""
        if isinstance(v, str):
            v = v.lower()
            if v not in ("even", "odd"):
                raise ValueError("parity_choice must be 'even' or 'odd'")
            return ParityChoice(v)
        return v


# --- Game Over ---
class GameResult(BaseModel):
    """Result details for a completed game."""

    status: GameResultStatus
    winner_player_id: Optional[str] = None
    drawn_number: int
    choices: dict[str, str]


class GameOver(BaseModel):
    """GAME_OVER message from Referee to Player."""

    protocol: str = "league.v2"
    message_type: str = "GAME_OVER"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: Optional[str] = None
    league_id: str
    round_id: int
    match_id: str
    game_result: GameResult


# --- League Standings Update ---
class StandingEntry(BaseModel):
    """Single entry in standings table."""

    rank: int
    player_id: str
    points: int
    wins: int = 0
    draws: int = 0
    losses: int = 0


class LeagueStandingsUpdate(BaseModel):
    """LEAGUE_STANDINGS_UPDATE message from Manager to Players."""

    protocol: str = "league.v2"
    message_type: str = "LEAGUE_STANDINGS_UPDATE"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    auth_token: Optional[str] = None
    league_id: str
    round_id: int
    standings: list[StandingEntry]
