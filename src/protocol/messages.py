"""
Protocol messages index.

Re-exports all message types for convenient imports.
"""

# Envelope and JSON-RPC
from .envelope import (
    MessageEnvelope,
    create_envelope,
    get_utc_timestamp,
    generate_conversation_id,
)
from .jsonrpc import (
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcError,
    create_jsonrpc_request,
    create_jsonrpc_response,
    create_error_response,
)

# Errors
from .errors import (
    ErrorCode,
    LeagueError,
    GameError,
    is_retryable,
    create_error_context,
    RETRYABLE_ERRORS,
)

# Registration
from .registration import (
    RegistrationStatus,
    PlayerMeta,
    LeagueRegisterRequest,
    LeagueRegisterResponse,
    create_register_request,
    parse_register_response,
)

# Game messages
from .game_messages import (
    ParityChoice,
    RoleInMatch,
    GameResultStatus,
    GameInvitationDetails,
    GameInvitation,
    GameJoinAck,
    ParityContext,
    ChooseParityCall,
    ChooseParityResponse,
    GameOver,
    GameResult,
    StandingEntry,
    LeagueStandingsUpdate,
)

# Query and completion messages
from .query_messages import (
    MatchAnnouncement,
    RoundAnnouncement,
    LeagueQuery,
    LeagueQueryResponse,
    RoundSummary,
    RoundCompleted,
    FinalStanding,
    LeagueSummary,
    LeagueCompleted,
)

__all__ = [
    # Envelope
    "MessageEnvelope",
    "create_envelope",
    "get_utc_timestamp",
    "generate_conversation_id",
    # JSON-RPC
    "JsonRpcRequest",
    "JsonRpcResponse",
    "JsonRpcError",
    "create_jsonrpc_request",
    "create_jsonrpc_response",
    "create_error_response",
    # Errors
    "ErrorCode",
    "LeagueError",
    "GameError",
    "is_retryable",
    "create_error_context",
    "RETRYABLE_ERRORS",
    # Registration
    "RegistrationStatus",
    "PlayerMeta",
    "LeagueRegisterRequest",
    "LeagueRegisterResponse",
    "create_register_request",
    "parse_register_response",
    # Game messages
    "ParityChoice",
    "RoleInMatch",
    "GameResultStatus",
    "GameInvitationDetails",
    "GameInvitation",
    "GameJoinAck",
    "ParityContext",
    "ChooseParityCall",
    "ChooseParityResponse",
    "GameOver",
    "GameResult",
    "StandingEntry",
    "LeagueStandingsUpdate",
    # Query/Completion
    "MatchAnnouncement",
    "RoundAnnouncement",
    "LeagueQuery",
    "LeagueQueryResponse",
    "RoundSummary",
    "RoundCompleted",
    "FinalStanding",
    "LeagueSummary",
    "LeagueCompleted",
]
