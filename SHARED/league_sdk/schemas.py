"""
Complete Pydantic models for all 18 league protocol message types.
"""

from typing import Optional, Literal
from pydantic import BaseModel

from .schemas_base import (
    MessageEnvelope,
    PlayerMeta,
    RefereeMeta,
    StandingEntry,
    ParityChoice,
    GameResult,
    MatchRole,
    ErrorCode,
)


# Registration Messages
class LeagueRegisterRequest(MessageEnvelope):
    """Player registration request."""
    message_type: Literal["LEAGUE_REGISTER_REQUEST"] = "LEAGUE_REGISTER_REQUEST"
    player_meta: PlayerMeta


class LeagueRegisterResponse(MessageEnvelope):
    """Player registration response."""
    message_type: Literal["LEAGUE_REGISTER_RESPONSE"] = "LEAGUE_REGISTER_RESPONSE"
    status: Literal["REGISTERED", "REJECTED"]
    player_id: Optional[str] = None
    auth_token: Optional[str] = None
    reason: Optional[str] = None


class RefereeRegisterRequest(MessageEnvelope):
    """Referee registration request."""
    message_type: Literal["REFEREE_REGISTER_REQUEST"] = "REFEREE_REGISTER_REQUEST"
    referee_meta: RefereeMeta


class RefereeRegisterResponse(MessageEnvelope):
    """Referee registration response."""
    message_type: Literal["REFEREE_REGISTER_RESPONSE"] = "REFEREE_REGISTER_RESPONSE"
    status: Literal["REGISTERED", "REJECTED"]
    referee_id: Optional[str] = None
    auth_token: Optional[str] = None


# Round Messages
class RoundAnnouncement(MessageEnvelope):
    """Round start announcement."""
    message_type: Literal["ROUND_ANNOUNCEMENT"] = "ROUND_ANNOUNCEMENT"
    round_id: str
    round_number: int
    matches: list[dict]  # List of {match_id, player_a, player_b, referee_id}


class RoundCompleted(MessageEnvelope):
    """Round completion notification."""
    message_type: Literal["ROUND_COMPLETED"] = "ROUND_COMPLETED"
    round_id: str
    round_number: int


# Match Messages
class GameInvitation(MessageEnvelope):
    """Game invitation to player."""
    message_type: Literal["GAME_INVITATION"] = "GAME_INVITATION"
    match_id: str
    round_id: str
    opponent_id: str
    role_in_match: MatchRole
    response_deadline: str


class GameJoinAck(MessageEnvelope):
    """Player's acknowledgment of game invitation."""
    message_type: Literal["GAME_JOIN_ACK"] = "GAME_JOIN_ACK"
    match_id: str
    status: Literal["ACCEPTED", "DECLINED"] = "ACCEPTED"


class ChooseParityCall(MessageEnvelope):
    """Request for parity choice."""
    message_type: Literal["CHOOSE_PARITY_CALL"] = "CHOOSE_PARITY_CALL"
    match_id: str
    deadline: str


class ChooseParityResponse(MessageEnvelope):
    """Player's parity choice."""
    message_type: Literal["CHOOSE_PARITY_RESPONSE"] = "CHOOSE_PARITY_RESPONSE"
    match_id: str
    parity_choice: ParityChoice


class GameOver(MessageEnvelope):
    """Game result notification."""
    message_type: Literal["GAME_OVER"] = "GAME_OVER"
    match_id: str
    drawn_number: int
    your_choice: ParityChoice
    opponent_choice: ParityChoice
    result: GameResult
    points_earned: int


class MatchResultReport(MessageEnvelope):
    """Referee's match result report to manager."""
    message_type: Literal["MATCH_RESULT_REPORT"] = "MATCH_RESULT_REPORT"
    match_id: str
    round_id: str
    player_a_id: str
    player_b_id: str
    player_a_choice: ParityChoice
    player_b_choice: ParityChoice
    drawn_number: int
    winner_id: Optional[str]
    player_a_result: GameResult
    player_b_result: GameResult


# Standings Messages
class LeagueStandingsUpdate(MessageEnvelope):
    """Standings update broadcast."""
    message_type: Literal["LEAGUE_STANDINGS_UPDATE"] = "LEAGUE_STANDINGS_UPDATE"
    standings: list[StandingEntry]
    round_id: Optional[str] = None


# Query Messages
class LeagueQuery(MessageEnvelope):
    """League information query."""
    message_type: Literal["LEAGUE_QUERY"] = "LEAGUE_QUERY"
    query_type: Literal["standings", "schedule", "stats", "next_match"]


class LeagueQueryResponse(MessageEnvelope):
    """League query response."""
    message_type: Literal["LEAGUE_QUERY_RESPONSE"] = "LEAGUE_QUERY_RESPONSE"
    query_type: str
    data: dict


# Completion Messages
class LeagueCompleted(MessageEnvelope):
    """League completion notification."""
    message_type: Literal["LEAGUE_COMPLETED"] = "LEAGUE_COMPLETED"
    final_standings: list[StandingEntry]
    total_rounds: int
    total_matches: int


# Error Messages
class LeagueError(MessageEnvelope):
    """League-level error."""
    message_type: Literal["LEAGUE_ERROR"] = "LEAGUE_ERROR"
    error_code: ErrorCode
    error_message: str
    retryable: bool = False


class GameError(MessageEnvelope):
    """Game-level error."""
    message_type: Literal["GAME_ERROR"] = "GAME_ERROR"
    match_id: Optional[str] = None
    error_code: ErrorCode
    error_message: str
    retryable: bool = False


# Health Messages
class AgentHeartbeat(MessageEnvelope):
    """Agent heartbeat for health monitoring."""
    message_type: Literal["AGENT_HEARTBEAT"] = "AGENT_HEARTBEAT"
    agent_type: Literal["player", "referee", "manager"]
    status: Literal["HEALTHY", "DEGRADED", "SHUTDOWN"]
    uptime_seconds: int
    matches_handled: Optional[int] = None
