"""
Type-safe configuration models using dataclasses.

Provides structured access to configuration data.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TimeoutConfig:
    """Timeout configuration in seconds."""
    registration: int = 10
    game_join_ack: int = 5
    parity_choice: int = 30
    match_result_report: int = 10
    league_query: int = 10


@dataclass
class RetryConfig:
    """Retry policy configuration."""
    max_retries: int = 3
    backoff_seconds: int = 2
    retryable_errors: list[str] = field(default_factory=lambda: ["E001", "E009"])


@dataclass
class ScoringConfig:
    """Scoring configuration."""
    win: int = 3
    draw: int = 1
    loss: int = 0


@dataclass
class SystemConfig:
    """System-wide configuration."""
    protocol_version: str = "league.v2"
    transport: str = "JSON-RPC 2.0"
    endpoint: str = "/mcp"
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    scoring: ScoringConfig = field(default_factory=ScoringConfig)


@dataclass
class AgentEndpoint:
    """Agent endpoint configuration."""
    id: str
    host: str
    port: int
    endpoint: str
    display_name: Optional[str] = None
    strategy: Optional[str] = None


@dataclass
class AgentsConfig:
    """All agents configuration."""
    league_manager: AgentEndpoint = field(default_factory=lambda: AgentEndpoint(
        id="MANAGER", host="127.0.0.1", port=8000, endpoint="http://127.0.0.1:8000/mcp"
    ))
    referees: list[AgentEndpoint] = field(default_factory=list)
    players: list[AgentEndpoint] = field(default_factory=list)


@dataclass
class AutoStartConfig:
    """Auto-start configuration."""
    enabled: bool = True
    min_players_to_start: int = 4
    wait_after_min_players_seconds: int = 10


@dataclass
class LeagueConfig:
    """League configuration."""
    league_id: str = "LEAGUE_2025"
    name: str = "Even/Odd Championship"
    season: str = "1"
    min_players: int = 2
    max_players: int = 8
    min_referees: int = 1
    rounds_per_matchup: int = 1
    parallel_matches: bool = True
    auto_start: AutoStartConfig = field(default_factory=AutoStartConfig)


def load_system_config(data: dict) -> SystemConfig:
    """Load SystemConfig from dictionary."""
    timeouts = TimeoutConfig(**data.get("timeouts", {}))
    retry = RetryConfig(**data.get("retry", {}))
    scoring = ScoringConfig(**data.get("scoring", {}))
    protocol = data.get("protocol", {})

    return SystemConfig(
        protocol_version=protocol.get("version", "league.v2"),
        transport=protocol.get("transport", "JSON-RPC 2.0"),
        endpoint=protocol.get("endpoint", "/mcp"),
        timeouts=timeouts,
        retry=retry,
        scoring=scoring,
    )


def load_agents_config(data: dict) -> AgentsConfig:
    """Load AgentsConfig from dictionary."""
    manager_data = data.get("league_manager", {})
    manager = AgentEndpoint(**manager_data) if manager_data else None

    referees = [AgentEndpoint(**r) for r in data.get("referees", [])]
    players = [AgentEndpoint(**p) for p in data.get("players", [])]

    return AgentsConfig(
        league_manager=manager,
        referees=referees,
        players=players,
    )
