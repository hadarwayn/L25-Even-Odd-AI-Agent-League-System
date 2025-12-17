"""
League simulation orchestration.
"""

import time
import asyncio
from typing import List, Dict, Any, Optional
from itertools import combinations

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.helpers import utc_now
from .player import Player
from .referee import Referee
from .output import print_standings as _print_standings


class LeagueSimulation:
    """Full league simulation with parallel execution support."""

    def __init__(self, parallel: bool = False):
        self.players: Dict[str, Player] = {}
        self.referees: Dict[str, Referee] = {}
        self.schedule: List[List[dict]] = []
        self.match_results: List[dict] = []
        self.activity_log: List[dict] = []
        self.parallel = parallel
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    def log(self, event_type: str, message: str, **kwargs) -> None:
        """Log activity."""
        entry = {
            "timestamp": utc_now(),
            "event": event_type,
            "message": message,
            **kwargs
        }
        self.activity_log.append(entry)
        print(f"[{entry['timestamp'][11:19]}] {event_type}: {message}")

    def register_referee(self, referee_id: str) -> None:
        """Register a referee."""
        referee = Referee(referee_id)
        self.referees[referee_id] = referee
        self.log("REFEREE_REGISTERED", f"{referee_id} registered")

    def register_player(self, player_id: str, display_name: str, strategy: str) -> None:
        """Register a player."""
        player = Player(player_id, display_name, strategy)
        self.players[player_id] = player
        self.log("PLAYER_REGISTERED", f"{player_id} ({display_name}) registered",
                 strategy=strategy)

    def generate_schedule(self) -> None:
        """Generate round-robin schedule."""
        player_ids = list(self.players.keys())
        all_matches = list(combinations(player_ids, 2))
        remaining = list(all_matches)
        round_num = 0

        while remaining:
            round_matches = []
            players_in_round = set()

            for match in remaining[:]:
                p1, p2 = match
                if p1 not in players_in_round and p2 not in players_in_round:
                    round_matches.append({
                        "match_id": f"R{round_num + 1}M{len(round_matches) + 1}",
                        "round_id": f"ROUND_{round_num + 1}",
                        "round_num": round_num + 1,
                        "player_a": p1,
                        "player_b": p2,
                    })
                    players_in_round.add(p1)
                    players_in_round.add(p2)
                    remaining.remove(match)

            if round_matches:
                self.schedule.append(round_matches)
                round_num += 1

        total_matches = sum(len(r) for r in self.schedule)
        self.log("SCHEDULE_GENERATED", f"{len(self.schedule)} rounds, {total_matches} matches")

    def _execute_match(self, match: dict, referee: Referee) -> dict:
        """Execute a single match."""
        player_a = self.players[match["player_a"]]
        player_b = self.players[match["player_b"]]
        return referee.conduct_match(player_a, player_b, match["match_id"])

    async def _run_round_parallel(self, round_matches: List[dict], round_num: int) -> None:
        """Run all matches in a round in parallel."""
        referee_ids = list(self.referees.keys())

        async def run_match(match: dict, idx: int) -> dict:
            referee = self.referees[referee_ids[idx % len(referee_ids)]]
            await asyncio.sleep(0.01)
            return self._execute_match(match, referee)

        tasks = [run_match(m, i) for i, m in enumerate(round_matches)]
        results = await asyncio.gather(*tasks)

        for result, match in zip(results, round_matches):
            result["round_num"] = round_num
            result["referee"] = referee_ids[round_matches.index(match) % len(referee_ids)]
            self.match_results.append(result)

            winner_str = result["winner"] if result["winner"] else "DRAW"
            self.log("MATCH_COMPLETED",
                     f"{match['match_id']}: {result['player_a']} vs {result['player_b']} -> {winner_str}",
                     drawn_number=result["drawn_number"])

    def run_league(self) -> None:
        """Run the entire league (sequential or parallel)."""
        self.start_time = time.perf_counter()
        self.log("LEAGUE_START", f"League starting (parallel={self.parallel})")

        if self.parallel:
            asyncio.run(self._run_league_async())
        else:
            self._run_league_sequential()

        self.end_time = time.perf_counter()
        duration_ms = (self.end_time - self.start_time) * 1000
        self.log("LEAGUE_COMPLETED", f"League finished in {duration_ms:.2f}ms")

    async def _run_league_async(self) -> None:
        """Run league with parallel match execution."""
        for round_idx, round_matches in enumerate(self.schedule):
            round_num = round_idx + 1
            self.log("ROUND_START", f"Round {round_num} starting (parallel)",
                     matches=len(round_matches))
            await self._run_round_parallel(round_matches, round_num)
            self.log("ROUND_COMPLETED", f"Round {round_num} completed")
            self.print_standings(f"After Round {round_num}")

    def _run_league_sequential(self) -> None:
        """Run league with sequential match execution."""
        referee_ids = list(self.referees.keys())

        for round_idx, round_matches in enumerate(self.schedule):
            round_num = round_idx + 1
            self.log("ROUND_START", f"Round {round_num} starting", matches=len(round_matches))

            for match_idx, match in enumerate(round_matches):
                referee_id = referee_ids[match_idx % len(referee_ids)]
                referee = self.referees[referee_id]

                result = self._execute_match(match, referee)
                result["round_num"] = round_num
                result["referee"] = referee_id
                self.match_results.append(result)

                winner_str = result["winner"] if result["winner"] else "DRAW"
                self.log("MATCH_COMPLETED",
                         f"{match['match_id']}: {result['player_a']} vs {result['player_b']} -> {winner_str}",
                         drawn_number=result["drawn_number"],
                         choices=f"{result['choice_a']}/{result['choice_b']}")

            self.log("ROUND_COMPLETED", f"Round {round_num} completed")
            self.print_standings(f"After Round {round_num}")

    def get_standings(self) -> List[Dict[str, Any]]:
        """Get current standings sorted by points."""
        standings = []
        for pid, player in self.players.items():
            standings.append({
                "rank": 0,
                "player_id": pid,
                "display_name": player.display_name,
                "strategy": player.strategy,
                "played": player.wins + player.draws + player.losses,
                "wins": player.wins,
                "draws": player.draws,
                "losses": player.losses,
                "points": player.points,
            })

        standings.sort(key=lambda x: (-x["points"], -x["wins"]))
        for i, s in enumerate(standings):
            s["rank"] = i + 1

        return standings

    def print_standings(self, title: str = "Standings") -> None:
        """Print standings table."""
        _print_standings(self.get_standings(), title)

    def get_performance_stats(self) -> dict:
        """Get performance statistics."""
        if not self.start_time or not self.end_time:
            return {}
        duration_ms = (self.end_time - self.start_time) * 1000
        return {
            "total_duration_ms": round(duration_ms, 2),
            "total_matches": len(self.match_results),
            "avg_match_time_ms": round(duration_ms / max(len(self.match_results), 1), 2),
            "parallel_mode": self.parallel,
        }
