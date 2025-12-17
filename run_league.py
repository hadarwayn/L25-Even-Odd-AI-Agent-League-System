"""
Full League Simulation - Runs a complete Even/Odd league with all agents.

This script simulates the entire league flow:
1. Registration of referees and players
2. Round-robin schedule generation
3. Match execution with all protocol messages
4. Standings calculation and final results
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timezone
from itertools import combinations

# Add SHARED to path
sys.path.insert(0, str(Path(__file__).parent / "SHARED"))

from league_sdk.game_rules import EvenOddGame
from league_sdk.helpers import utc_now, generate_uuid, generate_token


class Player:
    """Simulated player agent."""

    def __init__(self, player_id: str, display_name: str, strategy: str):
        self.player_id = player_id
        self.display_name = display_name
        self.strategy = strategy
        self.auth_token = generate_token()
        self.wins = 0
        self.draws = 0
        self.losses = 0
        self.points = 0
        self.history = []
        self._last_choice = "even"
        self._opponent_history = {}

    def choose_parity(self, opponent_id: str) -> str:
        """Choose parity based on strategy."""
        if self.strategy == "random":
            return random.choice(["even", "odd"])
        elif self.strategy == "deterministic_even":
            return "even"
        elif self.strategy == "deterministic_odd":
            return "odd"
        elif self.strategy == "alternating":
            choice = self._last_choice
            self._last_choice = "odd" if choice == "even" else "even"
            return choice
        elif self.strategy == "adaptive":
            # Check opponent history
            opp_hist = self._opponent_history.get(opponent_id, [])
            if len(opp_hist) < 2:
                return random.choice(["even", "odd"])
            even_count = opp_hist.count("even")
            odd_count = opp_hist.count("odd")
            return "even" if even_count >= odd_count else "odd"
        return random.choice(["even", "odd"])

    def record_result(self, result: str, opponent_id: str, opponent_choice: str):
        """Record match result."""
        if result == "WIN":
            self.wins += 1
            self.points += 3
        elif result == "DRAW":
            self.draws += 1
            self.points += 1
        else:
            self.losses += 1

        # Track opponent history for adaptive strategy
        if opponent_id not in self._opponent_history:
            self._opponent_history[opponent_id] = []
        self._opponent_history[opponent_id].append(opponent_choice)


class Referee:
    """Simulated referee agent."""

    def __init__(self, referee_id: str):
        self.referee_id = referee_id
        self.auth_token = generate_token()
        self.game = EvenOddGame()

    def conduct_match(self, player_a: Player, player_b: Player, match_id: str) -> dict:
        """Conduct a match between two players."""
        # Get choices
        choice_a = player_a.choose_parity(player_b.player_id)
        choice_b = player_b.choose_parity(player_a.player_id)

        # Determine outcome
        outcome = self.game.determine_match_outcome(
            player_a.player_id, choice_a,
            player_b.player_id, choice_b
        )

        # Record results
        player_a.record_result(outcome.player_a_result, player_b.player_id, choice_b)
        player_b.record_result(outcome.player_b_result, player_a.player_id, choice_a)

        return {
            "match_id": match_id,
            "player_a": player_a.player_id,
            "player_b": player_b.player_id,
            "choice_a": choice_a,
            "choice_b": choice_b,
            "drawn_number": outcome.drawn_number,
            "number_parity": outcome.number_parity,
            "result_a": outcome.player_a_result,
            "result_b": outcome.player_b_result,
            "winner": outcome.winner_id,
        }


class LeagueSimulation:
    """Full league simulation."""

    def __init__(self):
        self.players = {}
        self.referees = {}
        self.schedule = []
        self.match_results = []
        self.activity_log = []

    def log(self, event_type: str, message: str, **kwargs):
        """Log activity."""
        entry = {
            "timestamp": utc_now(),
            "event": event_type,
            "message": message,
            **kwargs
        }
        self.activity_log.append(entry)
        print(f"[{entry['timestamp'][11:19]}] {event_type}: {message}")

    def register_referee(self, referee_id: str):
        """Register a referee."""
        referee = Referee(referee_id)
        self.referees[referee_id] = referee
        self.log("REFEREE_REGISTERED", f"{referee_id} registered")

    def register_player(self, player_id: str, display_name: str, strategy: str):
        """Register a player."""
        player = Player(player_id, display_name, strategy)
        self.players[player_id] = player
        self.log("PLAYER_REGISTERED", f"{player_id} ({display_name}) registered",
                 strategy=strategy)

    def generate_schedule(self):
        """Generate round-robin schedule."""
        player_ids = list(self.players.keys())
        all_matches = list(combinations(player_ids, 2))

        # Distribute into rounds
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
        self.log("SCHEDULE_GENERATED",
                 f"{len(self.schedule)} rounds, {total_matches} matches")

    def run_league(self):
        """Run the entire league."""
        self.log("LEAGUE_START", "League starting")

        referee_ids = list(self.referees.keys())

        for round_idx, round_matches in enumerate(self.schedule):
            round_num = round_idx + 1
            self.log("ROUND_START", f"Round {round_num} starting",
                     matches=len(round_matches))

            for match_idx, match in enumerate(round_matches):
                # Assign referee (round-robin)
                referee_id = referee_ids[match_idx % len(referee_ids)]
                referee = self.referees[referee_id]

                player_a = self.players[match["player_a"]]
                player_b = self.players[match["player_b"]]

                # Conduct match
                result = referee.conduct_match(player_a, player_b, match["match_id"])
                result["round_num"] = round_num
                result["referee"] = referee_id
                self.match_results.append(result)

                # Log match result
                winner_str = result["winner"] if result["winner"] else "DRAW"
                self.log("MATCH_COMPLETED",
                         f"{match['match_id']}: {player_a.player_id} vs {player_b.player_id} -> {winner_str}",
                         drawn_number=result["drawn_number"],
                         choices=f"{result['choice_a']}/{result['choice_b']}")

            # Show standings after round
            self.log("ROUND_COMPLETED", f"Round {round_num} completed")
            self.print_standings(f"After Round {round_num}")

        self.log("LEAGUE_COMPLETED", "League finished")

    def get_standings(self):
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

    def print_standings(self, title: str = "Standings"):
        """Print standings table."""
        standings = self.get_standings()
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
        print(f"  {'Rank':<6}{'Player':<12}{'Strategy':<20}{'P':>4}{'W':>4}{'D':>4}{'L':>4}{'Pts':>5}")
        print(f"  {'-'*60}")
        for s in standings:
            print(f"  {s['rank']:<6}{s['player_id']:<12}{s['strategy']:<20}"
                  f"{s['played']:>4}{s['wins']:>4}{s['draws']:>4}{s['losses']:>4}{s['points']:>5}")
        print(f"{'='*70}\n")

    def print_match_history(self):
        """Print all match results."""
        print(f"\n{'='*80}")
        print("  MATCH HISTORY")
        print(f"{'='*80}")
        print(f"  {'Match':<8}{'Round':<7}{'Player A':<10}{'Choice':<8}{'vs':<4}{'Player B':<10}{'Choice':<8}{'Draw#':<6}{'Winner':<8}")
        print(f"  {'-'*75}")
        for m in self.match_results:
            winner = m['winner'] if m['winner'] else 'DRAW'
            print(f"  {m['match_id']:<8}{m['round_num']:<7}{m['player_a']:<10}{m['choice_a']:<8}"
                  f"{'vs':<4}{m['player_b']:<10}{m['choice_b']:<8}{m['drawn_number']:<6}{winner:<8}")
        print(f"{'='*80}\n")

    def print_activity_log(self):
        """Print activity log."""
        print(f"\n{'='*80}")
        print("  LEAGUE ACTIVITY LOG")
        print(f"{'='*80}")
        print(f"  {'Time':<12}{'Event':<25}{'Details':<40}")
        print(f"  {'-'*75}")
        for entry in self.activity_log:
            time_str = entry['timestamp'][11:19]
            print(f"  {time_str:<12}{entry['event']:<25}{entry['message']:<40}")
        print(f"{'='*80}\n")


def main():
    """Run the full league simulation."""
    print("\n" + "="*80)
    print("       EVEN/ODD AI AGENT LEAGUE - FULL SIMULATION")
    print("="*80 + "\n")

    # Create simulation
    sim = LeagueSimulation()

    # Register referees
    print("--- Registering Referees ---")
    sim.register_referee("REF01")
    sim.register_referee("REF02")

    # Register players with different strategies
    print("\n--- Registering Players ---")
    sim.register_player("P01", "AlphaBot", "random")
    sim.register_player("P02", "BetaBot", "deterministic_even")
    sim.register_player("P03", "GammaBot", "alternating")
    sim.register_player("P04", "DeltaBot", "adaptive")

    # Generate schedule
    print("\n--- Generating Schedule ---")
    sim.generate_schedule()

    # Run the league
    print("\n--- Running League ---")
    sim.run_league()

    # Print results
    sim.print_match_history()
    sim.print_activity_log()

    # Final standings
    print("\n" + "="*80)
    print("       FINAL RESULTS")
    print("="*80)
    sim.print_standings("FINAL STANDINGS")

    # Winner announcement
    standings = sim.get_standings()
    winner = standings[0]
    print(f"\n  CHAMPION: {winner['player_id']} ({winner['display_name']})")
    print(f"  Strategy: {winner['strategy']}")
    print(f"  Record: {winner['wins']}W-{winner['draws']}D-{winner['losses']}L ({winner['points']} points)")
    print("\n" + "="*80 + "\n")

    return sim


if __name__ == "__main__":
    main()
