"""
Player State Manager.

Tracks the player agent's lifecycle state, credentials, and match data.
Supports persistence to disk for restart recovery.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field, asdict


class AgentLifecycle(str, Enum):
    """
    Agent lifecycle states.

    INIT -> REGISTERED -> ACTIVE -> SHUTDOWN
                ^            |
                +-- SUSPENDED +
    """

    INIT = "INIT"
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    SHUTDOWN = "SHUTDOWN"


@dataclass
class MatchState:
    """State for a current match."""

    match_id: str
    league_id: str
    round_id: int
    opponent_id: str
    role: str  # PLAYER_A or PLAYER_B
    conversation_id: str
    choice: Optional[str] = None
    result: Optional[str] = None


@dataclass
class PlayerStats:
    """Player statistics."""

    wins: int = 0
    losses: int = 0
    draws: int = 0
    total_games: int = 0

    def add_result(self, result: str) -> None:
        """Update stats with a game result."""
        self.total_games += 1
        if result == "WIN":
            self.wins += 1
        elif result == "DRAW":
            self.draws += 1
        else:
            self.losses += 1


@dataclass
class PlayerState:
    """
    Complete state for a player agent.

    Tracks:
    - Lifecycle state
    - Registration credentials
    - Current match (if any)
    - Statistics
    """

    # Lifecycle
    lifecycle: AgentLifecycle = AgentLifecycle.INIT

    # Registration info (populated after successful registration)
    player_id: Optional[str] = None
    auth_token: Optional[str] = None
    league_id: Optional[str] = None

    # Current match state
    current_match: Optional[MatchState] = None

    # Statistics
    stats: PlayerStats = field(default_factory=PlayerStats)

    # Persistence path
    _data_dir: Optional[Path] = field(default=None, repr=False)

    def is_registered(self) -> bool:
        """Check if player is registered."""
        return self.lifecycle != AgentLifecycle.INIT and self.player_id is not None

    def can_play(self) -> bool:
        """Check if player can participate in games."""
        return self.lifecycle in (AgentLifecycle.REGISTERED, AgentLifecycle.ACTIVE)

    def register(
        self,
        player_id: str,
        auth_token: str,
        league_id: str,
    ) -> None:
        """
        Update state after successful registration.

        Args:
            player_id: Assigned player ID
            auth_token: Authentication token
            league_id: League identifier
        """
        self.player_id = player_id
        self.auth_token = auth_token
        self.league_id = league_id
        self.lifecycle = AgentLifecycle.REGISTERED
        self._persist()

    def start_match(
        self,
        match_id: str,
        round_id: int,
        opponent_id: str,
        role: str,
        conversation_id: str,
    ) -> None:
        """Start a new match."""
        self.current_match = MatchState(
            match_id=match_id,
            league_id=self.league_id or "",
            round_id=round_id,
            opponent_id=opponent_id,
            role=role,
            conversation_id=conversation_id,
        )
        self.lifecycle = AgentLifecycle.ACTIVE
        self._persist()

    def record_choice(self, choice: str) -> None:
        """Record the parity choice made."""
        if self.current_match:
            self.current_match.choice = choice
            self._persist()

    def end_match(self, result: str) -> None:
        """
        End the current match and update statistics.

        Args:
            result: WIN, DRAW, or TECHNICAL_LOSS
        """
        if self.current_match:
            self.current_match.result = result
            self.stats.add_result(result)
            self._save_match_history()
            self.current_match = None
            self.lifecycle = AgentLifecycle.REGISTERED
            self._persist()

    def suspend(self) -> None:
        """Mark player as suspended (not responding)."""
        self.lifecycle = AgentLifecycle.SUSPENDED
        self._persist()

    def recover(self) -> None:
        """Recover from suspended state."""
        if self.lifecycle == AgentLifecycle.SUSPENDED:
            self.lifecycle = AgentLifecycle.REGISTERED
            self._persist()

    def shutdown(self) -> None:
        """Mark player as shut down."""
        self.lifecycle = AgentLifecycle.SHUTDOWN
        self._persist()

    def set_data_dir(self, data_dir: str) -> None:
        """Set the data directory for persistence."""
        self._data_dir = Path(data_dir)

    def _get_state_file(self) -> Optional[Path]:
        """Get path to state persistence file."""
        if self._data_dir and self.player_id:
            player_dir = self._data_dir / self.player_id
            player_dir.mkdir(parents=True, exist_ok=True)
            return player_dir / "state.json"
        return None

    def _persist(self) -> None:
        """Save current state to disk."""
        state_file = self._get_state_file()
        if state_file:
            state_data = {
                "player_id": self.player_id,
                "auth_token": self.auth_token,
                "league_id": self.league_id,
                "lifecycle": self.lifecycle.value,
                "stats": asdict(self.stats),
            }
            try:
                with open(state_file, "w") as f:
                    json.dump(state_data, f, indent=2)
            except IOError:
                pass  # Don't crash if persistence fails

    def _save_match_history(self) -> None:
        """Append match result to history file."""
        if not self._data_dir or not self.player_id or not self.current_match:
            return

        history_file = self._data_dir / self.player_id / "history.json"

        # Load existing history
        history = []
        if history_file.exists():
            try:
                with open(history_file, "r") as f:
                    history = json.load(f)
            except (IOError, json.JSONDecodeError):
                history = []

        # Append current match
        history.append(asdict(self.current_match))

        # Save updated history
        try:
            with open(history_file, "w") as f:
                json.dump(history, f, indent=2)
        except IOError:
            pass

    @classmethod
    def load(cls, data_dir: str, player_id: str) -> "PlayerState":
        """
        Load player state from disk.

        Args:
            data_dir: Data directory path
            player_id: Player identifier

        Returns:
            Loaded PlayerState or new instance if not found
        """
        state = cls()
        state._data_dir = Path(data_dir)

        state_file = state._data_dir / player_id / "state.json"
        if state_file.exists():
            try:
                with open(state_file, "r") as f:
                    data = json.load(f)
                    state.player_id = data.get("player_id")
                    state.auth_token = data.get("auth_token")
                    state.league_id = data.get("league_id")
                    state.lifecycle = AgentLifecycle(data.get("lifecycle", "INIT"))

                    stats_data = data.get("stats", {})
                    state.stats = PlayerStats(**stats_data)
            except (IOError, json.JSONDecodeError):
                pass

        return state
