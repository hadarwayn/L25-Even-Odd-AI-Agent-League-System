"""
League SDK - Shared components for Even/Odd AI Agent League System.

Provides common functionality for League Manager, Referee, and Player agents.
"""

from .config_loader import ConfigLoader, get_config
from .config_models import SystemConfig, AgentsConfig, LeagueConfig
from .helpers import (
    utc_now,
    generate_uuid,
    generate_token,
    validate_utc,
    parse_sender,
    format_sender,
    is_retryable_error,
    calculate_points,
    determine_parity,
)
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
    AgentHeartbeat,
)
from .schemas_base import ParityChoice, GameResult, MatchRole, ErrorCode

# New modules
from .auth import (
    RateLimiter,
    AuthTokenValidator,
    requires_auth,
    sanitize_display_name,
    sanitize_metadata,
)
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpen,
    CircuitBreakerRegistry,
    CircuitState,
    with_circuit_breaker,
)
from .ring_buffer_logger import (
    RingBufferHandler,
    setup_ring_buffer_logger,
    get_log_status,
    print_log_status,
)
from .state_persistence import PersistedState, StateRepository as StatePersistence
from .benchmarks import (
    BenchmarkResult,
    PerformanceTimer,
    benchmark_sync,
    benchmark_async,
    timed,
    print_benchmark_results,
)
from .visualization import (
    MatchResult,
    PlayerStats,
    generate_standings_table,
    generate_match_history_table,
    generate_performance_chart,
    generate_strategy_comparison,
    save_results_json,
    load_results_json,
)

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
    "parse_sender",
    "format_sender",
    "is_retryable_error",
    "calculate_points",
    "determine_parity",
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
    "AgentHeartbeat",
    # Enums
    "ParityChoice",
    "GameResult",
    "MatchRole",
    "ErrorCode",
    # Auth & Security
    "RateLimiter",
    "AuthTokenValidator",
    "requires_auth",
    "sanitize_display_name",
    "sanitize_metadata",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerOpen",
    "CircuitBreakerRegistry",
    "CircuitState",
    "with_circuit_breaker",
    # Logging
    "RingBufferHandler",
    "setup_ring_buffer_logger",
    "get_log_status",
    "print_log_status",
    # State Persistence
    "PersistedState",
    "StatePersistence",
    # Benchmarks
    "BenchmarkResult",
    "PerformanceTimer",
    "benchmark_sync",
    "benchmark_async",
    "timed",
    "print_benchmark_results",
    # Visualization
    "MatchResult",
    "PlayerStats",
    "generate_standings_table",
    "generate_match_history_table",
    "generate_performance_chart",
    "generate_strategy_comparison",
    "save_results_json",
    "load_results_json",
]

__version__ = "1.1.0"
