"""
Player state management with persistence.
"""

import json
from pathlib import Path
from typing import Optional, Literal
from dataclasses import dataclass, field, asdict


AgentState = Literal["INIT", "REGISTERED", "ACTIVE", "SUSPENDED", "SHUTDOWN"]


@dataclass
class PlayerState:
    """Manages player state with persistence."""

    player_id: str
    state: AgentState = "INIT"
    assigned_id: Optional[str] = None
    auth_token: Optional[str] = None
    current_match_id: Optional[str] = None
    current_opponent_id: Optional[str] = None
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0
    history: list = field(default_factory=list)

    def __post_init__(self):
        """Load persisted state if available."""
        self._data_dir = Path(__file__).parent.parent.parent / "SHARED" / "data" / "state"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self._data_dir / f"{self.player_id}_state.json"
        self._load()

    def _load(self) -> None:
        """Load state from file."""
        if self._state_file.exists():
            try:
                with open(self._state_file, "r") as f:
                    data = json.load(f)
                self.state = data.get("state", "INIT")
                self.assigned_id = data.get("assigned_id")
                self.auth_token = data.get("auth_token")
                self.wins = data.get("wins", 0)
                self.draws = data.get("draws", 0)
                self.losses = data.get("losses", 0)
                self.points = data.get("points", 0)
                self.history = data.get("history", [])
            except Exception:
                pass

    def _save(self) -> None:
        """Save state to file."""
        data = {
            "player_id": self.player_id,
            "state": self.state,
            "assigned_id": self.assigned_id,
            "auth_token": self.auth_token,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "points": self.points,
            "history": self.history[-50:],  # Keep last 50 games
        }
        with open(self._state_file, "w") as f:
            json.dump(data, f, indent=2)

    def set_registered(self, assigned_id: str, auth_token: str) -> None:
        """Set registered state."""
        self.state = "REGISTERED"
        self.assigned_id = assigned_id
        self.auth_token = auth_token
        self._save()

    def set_active(self, match_id: str, opponent_id: str) -> None:
        """Set active state for a match."""
        self.state = "ACTIVE"
        self.current_match_id = match_id
        self.current_opponent_id = opponent_id
        self._save()

    def record_result(self, result: str, match_data: dict) -> None:
        """Record match result."""
        if result == "WIN":
            self.wins += 1
            self.points += 3
        elif result == "DRAW":
            self.draws += 1
            self.points += 1
        else:
            self.losses += 1

        self.history.append(match_data)
        self.state = "REGISTERED"
        self.current_match_id = None
        self.current_opponent_id = None
        self._save()

    def get_stats(self) -> dict:
        """Get player statistics."""
        total = self.wins + self.draws + self.losses
        return {
            "player_id": self.assigned_id or self.player_id,
            "total_games": total,
            "wins": self.wins,
            "draws": self.draws,
            "losses": self.losses,
            "points": self.points,
            "win_rate": round(self.wins / total, 2) if total > 0 else 0,
        }

    def is_registered(self) -> bool:
        """Check if player is registered."""
        return self.state in ("REGISTERED", "ACTIVE")
