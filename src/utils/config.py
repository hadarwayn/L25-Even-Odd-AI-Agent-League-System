"""
Configuration loader for the Player Agent.

Loads settings from YAML files and environment variables.
Environment variables override YAML settings.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import yaml
from dotenv import load_dotenv


@dataclass
class AgentConfig:
    """Agent identity configuration."""

    display_name: str = "AgentAlpha"
    version: str = "1.0.0"
    protocol_version: str = "2.1.0"
    game_types: list[str] = field(default_factory=lambda: ["even_odd"])


@dataclass
class ServerConfig:
    """HTTP server configuration."""

    host: str = "127.0.0.1"
    port: int = 8101


@dataclass
class LeagueManagerConfig:
    """League Manager connection configuration."""

    endpoint: str = "http://localhost:8000/mcp"


@dataclass
class TimeoutConfig:
    """Timeout settings for different operations."""

    registration: int = 10
    game_join: int = 5
    parity_choice: int = 30
    default: int = 10


@dataclass
class RetryConfig:
    """Retry policy configuration."""

    max_retries: int = 3
    backoff_seconds: int = 2


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    directory: str = "logs/agents"


@dataclass
class DataConfig:
    """Data persistence configuration."""

    players_directory: str = "data/players"


@dataclass
class Config:
    """Complete configuration for the Player Agent."""

    agent: AgentConfig = field(default_factory=AgentConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    league_manager: LeagueManagerConfig = field(default_factory=LeagueManagerConfig)
    timeouts: TimeoutConfig = field(default_factory=TimeoutConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    data: DataConfig = field(default_factory=DataConfig)


def _get_project_root() -> Path:
    """Get project root directory."""
    return Path(__file__).resolve().parent.parent.parent


def load_config(
    config_path: Optional[str] = None,
    load_env: bool = True,
) -> Config:
    """
    Load configuration from YAML and environment variables.

    Args:
        config_path: Path to YAML config file (default: config/settings.yaml)
        load_env: Whether to load .env file

    Returns:
        Config object with all settings
    """
    project_root = _get_project_root()

    # Load .env file if present
    if load_env:
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)

    # Load YAML config
    if config_path is None:
        config_path = project_root / "config" / "settings.yaml"
    else:
        config_path = Path(config_path)

    yaml_config = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            yaml_config = yaml.safe_load(f) or {}

    # Build config with env overrides
    config = Config()

    # Agent settings
    agent_yaml = yaml_config.get("agent", {})
    config.agent = AgentConfig(
        display_name=os.getenv("PLAYER_NAME", agent_yaml.get("display_name", "AgentAlpha")),
        version=os.getenv("AGENT_VERSION", agent_yaml.get("version", "1.0.0")),
        protocol_version=os.getenv("PROTOCOL_VERSION", agent_yaml.get("protocol_version", "2.1.0")),
        game_types=agent_yaml.get("game_types", ["even_odd"]),
    )

    # Server settings
    server_yaml = yaml_config.get("server", {})
    config.server = ServerConfig(
        host=server_yaml.get("host", "127.0.0.1"),
        port=int(os.getenv("PLAYER_PORT", server_yaml.get("port", 8101))),
    )

    # League Manager settings
    lm_yaml = yaml_config.get("league_manager", {})
    config.league_manager = LeagueManagerConfig(
        endpoint=os.getenv("LEAGUE_MANAGER_URL", lm_yaml.get("endpoint", "http://localhost:8000/mcp")),
    )

    # Timeout settings
    timeout_yaml = yaml_config.get("timeouts", {})
    config.timeouts = TimeoutConfig(
        registration=timeout_yaml.get("registration", 10),
        game_join=timeout_yaml.get("game_join", 5),
        parity_choice=timeout_yaml.get("parity_choice", 30),
        default=timeout_yaml.get("default", 10),
    )

    # Retry settings
    retry_yaml = yaml_config.get("retry", {})
    config.retry = RetryConfig(
        max_retries=retry_yaml.get("max_retries", 3),
        backoff_seconds=retry_yaml.get("backoff_seconds", 2),
    )

    # Logging settings
    logging_yaml = yaml_config.get("logging", {})
    config.logging = LoggingConfig(
        level=os.getenv("LOG_LEVEL", logging_yaml.get("level", "INFO")),
        directory=logging_yaml.get("directory", "logs/agents"),
    )

    # Data settings
    data_yaml = yaml_config.get("data", {})
    config.data = DataConfig(
        players_directory=data_yaml.get("players_directory", "data/players"),
    )

    return config


def get_contact_endpoint(config: Config) -> str:
    """Generate the contact endpoint URL for this agent."""
    return f"http://{config.server.host}:{config.server.port}/mcp"
