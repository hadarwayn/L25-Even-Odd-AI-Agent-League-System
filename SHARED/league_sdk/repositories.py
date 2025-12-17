"""
Data repositories for the league system.

Provides persistence for standings, matches, and agent state.
"""

import json
from pathlib import Path
from typing import Any, Optional
from datetime import datetime, timezone


class BaseRepository:
    """Base repository with JSON persistence."""

    def __init__(self, data_dir: str, filename: str):
        """Initialize repository."""
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._filepath = self._data_dir / filename
        self._data: dict[str, Any] = self._load()

    def _load(self) -> dict[str, Any]:
        """Load data from file."""
        if self._filepath.exists():
            with open(self._filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(self) -> None:
        """Save data to file."""
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, indent=2, default=str)


class StandingsRepository(BaseRepository):
    """Repository for league standings."""

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize standings repository."""
        if not data_dir:
            data_dir = str(Path(__file__).parent.parent / "data" / "standings")
        super().__init__(data_dir, "standings.json")

    def get_standings(self) -> list[dict[str, Any]]:
        """Get current standings sorted by points."""
        standings = list(self._data.get("players", {}).values())
        return sorted(standings, key=lambda x: (-x.get("points", 0), -x.get("wins", 0)))

    def update_player(self, player_id: str, result: str) -> None:
        """Update player standings after a match."""
        if "players" not in self._data:
            self._data["players"] = {}

        if player_id not in self._data["players"]:
            self._data["players"][player_id] = {
                "player_id": player_id,
                "points": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "played": 0,
            }

        player = self._data["players"][player_id]
        player["played"] += 1

        if result == "WIN":
            player["wins"] += 1
            player["points"] += 3
        elif result == "DRAW":
            player["draws"] += 1
            player["points"] += 1
        else:
            player["losses"] += 1

        self._save()

    def reset(self) -> None:
        """Reset all standings."""
        self._data = {"players": {}}
        self._save()


class MatchRepository(BaseRepository):
    """Repository for match history."""

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize match repository."""
        if not data_dir:
            data_dir = str(Path(__file__).parent.parent / "data" / "matches")
        super().__init__(data_dir, "matches.json")

    def add_match(self, match_data: dict[str, Any]) -> None:
        """Add a match result."""
        if "matches" not in self._data:
            self._data["matches"] = []

        match_data["recorded_at"] = datetime.now(timezone.utc).isoformat()
        self._data["matches"].append(match_data)
        self._save()

    def get_matches(self, round_id: Optional[str] = None) -> list[dict[str, Any]]:
        """Get matches, optionally filtered by round."""
        matches = self._data.get("matches", [])
        if round_id:
            matches = [m for m in matches if m.get("round_id") == round_id]
        return matches

    def get_player_history(self, player_id: str) -> list[dict[str, Any]]:
        """Get match history for a player."""
        return [
            m for m in self._data.get("matches", [])
            if player_id in (m.get("player_a"), m.get("player_b"))
        ]


class StateRepository(BaseRepository):
    """Repository for agent state persistence."""

    def __init__(self, agent_id: str, data_dir: Optional[str] = None):
        """Initialize state repository."""
        if not data_dir:
            data_dir = str(Path(__file__).parent.parent / "data" / "state")
        super().__init__(data_dir, f"{agent_id}_state.json")

    def get(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a state value."""
        self._data[key] = value
        self._save()

    def get_all(self) -> dict[str, Any]:
        """Get all state data."""
        return self._data.copy()
