"""
Standings manager for the league.

Calculates and maintains league standings.
"""

from typing import Optional
from dataclasses import dataclass, field


@dataclass
class PlayerStanding:
    """Player standings entry."""
    player_id: str
    display_name: str = ""
    points: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    played: int = 0


class StandingsManager:
    """Manages league standings."""

    def __init__(self):
        """Initialize standings manager."""
        self.standings: dict[str, PlayerStanding] = {}
        self.scoring = {"WIN": 3, "DRAW": 1, "LOSS": 0, "TECHNICAL_LOSS": 0}

    def register_player(self, player_id: str, display_name: str = "") -> None:
        """Register a player in standings."""
        if player_id not in self.standings:
            self.standings[player_id] = PlayerStanding(
                player_id=player_id,
                display_name=display_name or player_id,
            )

    def update_result(self, player_id: str, result: str) -> None:
        """
        Update standings for a player after a match.

        Args:
            player_id: Player identifier
            result: WIN, DRAW, LOSS, or TECHNICAL_LOSS
        """
        if player_id not in self.standings:
            self.register_player(player_id)

        standing = self.standings[player_id]
        standing.played += 1
        standing.points += self.scoring.get(result, 0)

        if result == "WIN":
            standing.wins += 1
        elif result == "DRAW":
            standing.draws += 1
        else:
            standing.losses += 1

    def get_standings(self) -> list[dict]:
        """
        Get sorted standings.

        Returns:
            List of standings sorted by points (desc), wins (desc)
        """
        sorted_standings = sorted(
            self.standings.values(),
            key=lambda x: (-x.points, -x.wins),
        )

        return [
            {
                "rank": i + 1,
                "player_id": s.player_id,
                "display_name": s.display_name,
                "points": s.points,
                "wins": s.wins,
                "draws": s.draws,
                "losses": s.losses,
                "played": s.played,
            }
            for i, s in enumerate(sorted_standings)
        ]

    def get_player_standing(self, player_id: str) -> Optional[dict]:
        """Get standing for a specific player."""
        standings = self.get_standings()
        for s in standings:
            if s["player_id"] == player_id:
                return s
        return None

    def get_leader(self) -> Optional[dict]:
        """Get current leader."""
        standings = self.get_standings()
        return standings[0] if standings else None

    def reset(self) -> None:
        """Reset all standings."""
        for standing in self.standings.values():
            standing.points = 0
            standing.wins = 0
            standing.draws = 0
            standing.losses = 0
            standing.played = 0

    def get_stats(self) -> dict:
        """Get overall league statistics."""
        total_matches = sum(s.played for s in self.standings.values()) // 2
        total_wins = sum(s.wins for s in self.standings.values())
        total_draws = sum(s.draws for s in self.standings.values()) // 2

        return {
            "total_players": len(self.standings),
            "total_matches_played": total_matches,
            "total_wins": total_wins,
            "total_draws": total_draws,
            "leader": self.get_leader(),
        }
