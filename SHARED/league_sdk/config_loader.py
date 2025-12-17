"""
Configuration loader with lazy loading and caching.

Loads JSON configuration files from SHARED/config/.
"""

import json
from pathlib import Path
from typing import Optional, Any
from functools import lru_cache


class ConfigLoader:
    """Lazy-loading configuration manager with caching."""

    _instance: Optional["ConfigLoader"] = None
    _cache: dict[str, Any] = {}

    def __new__(cls) -> "ConfigLoader":
        """Singleton pattern for config loader."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._cache = {}
        return cls._instance

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config loader.

        Args:
            config_dir: Path to config directory. Defaults to SHARED/config/
        """
        if config_dir:
            self._config_dir = Path(config_dir)
        else:
            # Find SHARED/config relative to this file
            sdk_dir = Path(__file__).parent
            self._config_dir = sdk_dir.parent / "config"

    def _load_file(self, filename: str) -> dict[str, Any]:
        """Load and cache a JSON config file."""
        if filename in self._cache:
            return self._cache[filename]

        filepath = self._config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._cache[filename] = data
        return data

    @property
    def system(self) -> dict[str, Any]:
        """Get system configuration."""
        return self._load_file("system.json")

    @property
    def agents(self) -> dict[str, Any]:
        """Get agents configuration."""
        return self._load_file("agents.json")

    @property
    def league(self) -> dict[str, Any]:
        """Get league configuration."""
        return self._load_file("league.json")

    def get_timeout(self, name: str) -> int:
        """Get a timeout value by name."""
        return self.system.get("timeouts", {}).get(name, 10)

    def get_player_config(self, player_id: str) -> Optional[dict[str, Any]]:
        """Get configuration for a specific player."""
        for player in self.agents.get("players", []):
            if player["id"] == player_id:
                return player
        return None

    def get_referee_config(self, referee_id: str) -> Optional[dict[str, Any]]:
        """Get configuration for a specific referee."""
        for referee in self.agents.get("referees", []):
            if referee["id"] == referee_id:
                return referee
        return None

    def clear_cache(self) -> None:
        """Clear the configuration cache."""
        self._cache.clear()


# Convenience function
def get_config() -> ConfigLoader:
    """Get the singleton config loader instance."""
    return ConfigLoader()
