"""
League SDK - Shared components for Even/Odd AI Agent League System.

Provides common functionality for League Manager, Referee, and Player agents.
"""

from .config_loader import ConfigLoader, get_config
from .config_models import SystemConfig, AgentsConfig, LeagueConfig
from .helpers import utc_now, generate_uuid, generate_token, validate_utc
from .logger import JsonLogger
from .mcp_client import MCPClient
from .mcp_server import MCPServer
from .repositories import StandingsRepository, MatchRepository, StateRepository
from .schemas import (
    LeagueRegisterRequest,
    LeagueRegisterResponse,
    RefereeRegisterRequest,
    RefereeRegisterResponse,
    RoundAnnouncement,
    RoundCompleted,
    GameInvitation,
    GameJoinAck,
    ChooseParityCall,
    ChooseParityResponse,
    GameOver,
    MatchResultReport,
    LeagueStandingsUpdate,
    LeagueQuery,
    LeagueQueryResponse,
    LeagueCompleted,
    LeagueError,
    GameError,
)
from .schemas_base import ParityChoice, GameResult, MatchRole, ErrorCode

__all__ = [
    # Config
    "ConfigLoader",
    "get_config",
    "SystemConfig",
    "AgentsConfig",
    "LeagueConfig",
    # Helpers
    "utc_now",
    "generate_uuid",
    "generate_token",
    "validate_utc",
    # Core
    "JsonLogger",
    "MCPClient",
    "MCPServer",
    # Repositories
    "StandingsRepository",
    "MatchRepository",
    "StateRepository",
    # Schemas
    "LeagueRegisterRequest",
    "LeagueRegisterResponse",
    "RefereeRegisterRequest",
    "RefereeRegisterResponse",
    "RoundAnnouncement",
    "RoundCompleted",
    "GameInvitation",
    "GameJoinAck",
    "ChooseParityCall",
    "ChooseParityResponse",
    "GameOver",
    "MatchResultReport",
    "LeagueStandingsUpdate",
    "LeagueQuery",
    "LeagueQueryResponse",
    "LeagueCompleted",
    "LeagueError",
    "GameError",
    # Enums
    "ParityChoice",
    "GameResult",
    "MatchRole",
    "ErrorCode",
]

__version__ = "1.0.0"
