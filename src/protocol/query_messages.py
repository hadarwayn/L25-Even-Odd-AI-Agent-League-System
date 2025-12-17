"""
Query and completion message models for league.v2 protocol.

Handles:
- LEAGUE_QUERY / LEAGUE_QUERY_RESPONSE
- ROUND_ANNOUNCEMENT
- ROUND_COMPLETED
- LEAGUE_COMPLETED
"""

from typing import Any, Optional
from pydantic import BaseModel


# --- Round Announcement ---
class MatchAnnouncement(BaseModel):
    """Single match in a round announcement."""

    match_id: str
    game_type: str = "even_odd"
    player_A_id: str
    player_B_id: str
    referee_endpoint: str


class RoundAnnouncement(BaseModel):
    """ROUND_ANNOUNCEMENT message from Manager to all agents."""

    protocol: str = "league.v2"
    message_type: str = "ROUND_ANNOUNCEMENT"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    league_id: str
    round_id: int
    matches: list[MatchAnnouncement]


# --- League Query ---
class LeagueQuery(BaseModel):
    """LEAGUE_QUERY message from Player to Manager."""

    protocol: str = "league.v2"
    message_type: str = "LEAGUE_QUERY"
    sender: str
    timestamp: str
    conversation_id: str
    auth_token: str
    league_id: str
    query_type: str  # e.g., "standings", "schedule"


class LeagueQueryResponse(BaseModel):
    """LEAGUE_QUERY_RESPONSE message from Manager to Player."""

    protocol: str = "league.v2"
    message_type: str = "LEAGUE_QUERY_RESPONSE"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    league_id: str
    query_type: str
    result: dict[str, Any]


# --- Round Completed ---
class RoundSummary(BaseModel):
    """Summary of a completed round."""

    total_matches: int
    completed_matches: int
    failed_matches: int = 0


class RoundCompleted(BaseModel):
    """ROUND_COMPLETED message from Manager to all agents."""

    protocol: str = "league.v2"
    message_type: str = "ROUND_COMPLETED"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    league_id: str
    round_id: int
    summary: RoundSummary


# --- League Completed ---
class FinalStanding(BaseModel):
    """Final standing entry at league completion."""

    rank: int
    player_id: str
    points: int
    wins: int = 0
    draws: int = 0
    losses: int = 0


class LeagueSummary(BaseModel):
    """Summary of the completed league."""

    total_rounds: int
    total_matches: int
    total_completed: int


class LeagueCompleted(BaseModel):
    """LEAGUE_COMPLETED message from Manager to all agents."""

    protocol: str = "league.v2"
    message_type: str = "LEAGUE_COMPLETED"
    sender: str = "league_manager"
    timestamp: str
    conversation_id: str
    league_id: str
    final_standings: list[FinalStanding]
    summary: LeagueSummary
