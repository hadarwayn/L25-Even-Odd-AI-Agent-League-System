"""
Round-robin scheduler for the league.

Generates match schedules and assigns referees.
"""

from typing import Optional
from itertools import combinations


class Scheduler:
    """Round-robin match scheduler."""

    def __init__(self):
        """Initialize scheduler."""
        self.schedule: list[list[dict]] = []  # rounds -> matches
        self.current_round: int = 0
        self.player_ids: list[str] = []

    def generate_schedule(self, player_ids: list[str]) -> list[list[dict]]:
        """
        Generate round-robin schedule.

        Args:
            player_ids: List of player IDs

        Returns:
            Schedule as list of rounds, each containing matches
        """
        self.player_ids = player_ids
        self.schedule = []
        self.current_round = 0

        n = len(player_ids)
        if n < 2:
            return []

        # Generate all possible pairings
        all_matches = list(combinations(player_ids, 2))

        # Distribute matches into rounds
        # Each player plays at most once per round
        remaining = list(all_matches)
        round_num = 0

        while remaining:
            round_matches = []
            players_in_round: set[str] = set()

            for match in remaining[:]:
                p1, p2 = match
                if p1 not in players_in_round and p2 not in players_in_round:
                    round_matches.append({
                        "match_id": f"R{round_num + 1}M{len(round_matches) + 1}",
                        "round_id": f"ROUND_{round_num + 1}",
                        "player_a": p1,
                        "player_b": p2,
                        "referee_id": None,  # Assigned later
                    })
                    players_in_round.add(p1)
                    players_in_round.add(p2)
                    remaining.remove(match)

            if round_matches:
                self.schedule.append(round_matches)
                round_num += 1

        return self.schedule

    def assign_referees(self, referee_ids: list[str]) -> None:
        """
        Assign referees to matches (load-balanced).

        Args:
            referee_ids: List of available referee IDs
        """
        if not referee_ids:
            return

        ref_idx = 0
        for round_matches in self.schedule:
            for match in round_matches:
                match["referee_id"] = referee_ids[ref_idx % len(referee_ids)]
                ref_idx += 1

    def get_current_round(self) -> Optional[list[dict]]:
        """Get matches for current round."""
        if self.current_round < len(self.schedule):
            return self.schedule[self.current_round]
        return None

    def advance_round(self) -> bool:
        """
        Advance to next round.

        Returns:
            True if there's another round, False if league is complete
        """
        self.current_round += 1
        return self.current_round < len(self.schedule)

    def get_total_rounds(self) -> int:
        """Get total number of rounds."""
        return len(self.schedule)

    def get_total_matches(self) -> int:
        """Get total number of matches."""
        return sum(len(r) for r in self.schedule)

    def get_player_next_match(self, player_id: str) -> Optional[dict]:
        """Get next match for a player."""
        for round_idx in range(self.current_round, len(self.schedule)):
            for match in self.schedule[round_idx]:
                if player_id in (match["player_a"], match["player_b"]):
                    return match
        return None

    def get_schedule_summary(self) -> dict:
        """Get schedule summary."""
        return {
            "total_rounds": len(self.schedule),
            "total_matches": self.get_total_matches(),
            "current_round": self.current_round + 1,
            "players": self.player_ids,
            "rounds": [
                {
                    "round_number": i + 1,
                    "round_id": f"ROUND_{i + 1}",
                    "matches": len(r),
                }
                for i, r in enumerate(self.schedule)
            ],
        }
