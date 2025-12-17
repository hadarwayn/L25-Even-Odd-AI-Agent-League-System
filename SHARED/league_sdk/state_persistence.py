"""
State persistence for player agents.

Provides file-based persistence for player state to enable
restart recovery and state auditing.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional, Dict
from dataclasses import dataclass, asdict


@dataclass
class PersistedState:
    """Persisted player state structure."""
    player_id: str
    auth_token: Optional[str] = None
    registered: bool = False
    wins: int = 0
    draws: int = 0
    losses: int = 0
    points: int = 0
    current_match_id: Optional[str] = None
    current_opponent_id: Optional[str] = None
    last_choice: Optional[str] = None
    last_updated: Optional[str] = None
    match_history: list = None

    def __post_init__(self):
        if self.match_history is None:
            self.match_history = []


class StateRepository:
    """
    File-based state persistence repository.

    Stores player state as JSON files for restart recovery.
    """

    def __init__(
        self,
        agent_id: str,
        state_dir: Optional[Path] = None,
    ):
        """
        Initialize state repository.

        Args:
            agent_id: Agent identifier
            state_dir: Directory for state files. Defaults to SHARED/data/state/
        """
        self.agent_id = agent_id

        if state_dir:
            self._state_dir = Path(state_dir)
        else:
            sdk_dir = Path(__file__).parent
            self._state_dir = sdk_dir.parent / "data" / "state"

        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._state_file = self._state_dir / f"{agent_id}.state.json"

    def _timestamp(self) -> str:
        """Get current UTC timestamp."""
        return datetime.now(timezone.utc).isoformat()

    def save(self, state: PersistedState) -> None:
        """
        Save state to file.

        Args:
            state: State to persist
        """
        state.last_updated = self._timestamp()
        data = asdict(state)

        with open(self._state_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def load(self) -> Optional[PersistedState]:
        """
        Load state from file.

        Returns:
            Loaded state or None if no state file exists
        """
        if not self._state_file.exists():
            return None

        try:
            with open(self._state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return PersistedState(**data)
        except (json.JSONDecodeError, TypeError) as e:
            # Corrupted state file, return None
            return None

    def delete(self) -> None:
        """Delete the state file."""
        if self._state_file.exists():
            self._state_file.unlink()

    def exists(self) -> bool:
        """Check if state file exists."""
        return self._state_file.exists()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific value from state."""
        state = self.load()
        if state is None:
            return default
        return getattr(state, key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a specific value in state."""
        state = self.load()
        if state is None:
            state = PersistedState(player_id=self.agent_id)
        setattr(state, key, value)
        self.save(state)

    def update_match_result(
        self,
        match_id: str,
        opponent_id: str,
        result: str,
        choice: str,
        opponent_choice: str,
        drawn_number: int,
    ) -> None:
        """
        Update state with match result.

        Args:
            match_id: Match identifier
            opponent_id: Opponent player ID
            result: WIN, DRAW, LOSS
            choice: Player's parity choice
            opponent_choice: Opponent's parity choice
            drawn_number: The drawn number
        """
        state = self.load()
        if state is None:
            state = PersistedState(player_id=self.agent_id)

        # Update stats
        if result == "WIN":
            state.wins += 1
            state.points += 3
        elif result == "DRAW":
            state.draws += 1
            state.points += 1
        else:
            state.losses += 1

        # Clear current match
        state.current_match_id = None
        state.current_opponent_id = None
        state.last_choice = choice

        # Add to history
        state.match_history.append({
            "match_id": match_id,
            "opponent_id": opponent_id,
            "result": result,
            "choice": choice,
            "opponent_choice": opponent_choice,
            "drawn_number": drawn_number,
            "timestamp": self._timestamp(),
        })

        self.save(state)

    def start_match(self, match_id: str, opponent_id: str) -> None:
        """Record match start."""
        state = self.load()
        if state is None:
            state = PersistedState(player_id=self.agent_id)

        state.current_match_id = match_id
        state.current_opponent_id = opponent_id
        self.save(state)

    def get_stats(self) -> Dict[str, int]:
        """Get player statistics."""
        state = self.load()
        if state is None:
            return {"wins": 0, "draws": 0, "losses": 0, "points": 0}

        return {
            "wins": state.wins,
            "draws": state.draws,
            "losses": state.losses,
            "points": state.points,
        }
