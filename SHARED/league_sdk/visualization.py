"""
Visualization utilities for league results.

Provides functions for generating performance graphs and result charts.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class MatchResult:
    """Single match result."""
    match_id: str
    round_num: int
    player_a: str
    player_b: str
    choice_a: str
    choice_b: str
    drawn_number: int
    winner: Optional[str]


@dataclass
class PlayerStats:
    """Player statistics."""
    player_id: str
    display_name: str
    strategy: str
    wins: int
    draws: int
    losses: int
    points: int


def generate_standings_table(standings: List[PlayerStats]) -> str:
    """
    Generate ASCII standings table.

    Args:
        standings: List of player statistics sorted by rank

    Returns:
        Formatted ASCII table string
    """
    lines = []
    lines.append("=" * 70)
    lines.append("  STANDINGS")
    lines.append("=" * 70)
    lines.append(f"  {'Rank':<6}{'Player':<12}{'Strategy':<20}{'W':>4}{'D':>4}{'L':>4}{'Pts':>5}")
    lines.append(f"  {'-'*62}")

    for i, s in enumerate(standings, 1):
        lines.append(
            f"  {i:<6}{s.player_id:<12}{s.strategy:<20}"
            f"{s.wins:>4}{s.draws:>4}{s.losses:>4}{s.points:>5}"
        )

    lines.append("=" * 70)
    return "\n".join(lines)


def generate_match_history_table(matches: List[MatchResult]) -> str:
    """
    Generate ASCII match history table.

    Args:
        matches: List of match results

    Returns:
        Formatted ASCII table string
    """
    lines = []
    lines.append("=" * 80)
    lines.append("  MATCH HISTORY")
    lines.append("=" * 80)
    lines.append(
        f"  {'Match':<8}{'Round':<7}{'Player A':<10}{'Choice':<8}"
        f"{'vs':<4}{'Player B':<10}{'Choice':<8}{'#':>4}{'Winner':<8}"
    )
    lines.append(f"  {'-'*75}")

    for m in matches:
        winner = m.winner if m.winner else "DRAW"
        lines.append(
            f"  {m.match_id:<8}{m.round_num:<7}{m.player_a:<10}{m.choice_a:<8}"
            f"{'vs':<4}{m.player_b:<10}{m.choice_b:<8}{m.drawn_number:>4}  {winner:<8}"
        )

    lines.append("=" * 80)
    return "\n".join(lines)


def generate_performance_chart(results: Dict[str, Any]) -> str:
    """
    Generate ASCII bar chart of performance metrics.

    Args:
        results: Dictionary of metric name to values

    Returns:
        ASCII bar chart string
    """
    lines = []
    lines.append("\n  PERFORMANCE METRICS")
    lines.append("  " + "-" * 50)

    max_val = max(results.values()) if results else 1

    for name, value in results.items():
        bar_len = int((value / max_val) * 40) if max_val > 0 else 0
        bar = "#" * bar_len
        lines.append(f"  {name:<15} |{bar:<40}| {value:.2f}")

    lines.append("  " + "-" * 50)
    return "\n".join(lines)


def generate_strategy_comparison(stats: List[PlayerStats]) -> str:
    """
    Generate strategy comparison table.

    Args:
        stats: List of player statistics

    Returns:
        Formatted comparison string
    """
    lines = []
    lines.append("\n  STRATEGY PERFORMANCE")
    lines.append("  " + "=" * 50)

    # Group by strategy
    by_strategy: Dict[str, List[PlayerStats]] = {}
    for s in stats:
        if s.strategy not in by_strategy:
            by_strategy[s.strategy] = []
        by_strategy[s.strategy].append(s)

    for strategy, players in sorted(by_strategy.items()):
        total_wins = sum(p.wins for p in players)
        total_draws = sum(p.draws for p in players)
        total_losses = sum(p.losses for p in players)
        total_points = sum(p.points for p in players)

        lines.append(f"\n  {strategy}:")
        lines.append(f"    Wins: {total_wins}, Draws: {total_draws}, Losses: {total_losses}")
        lines.append(f"    Total Points: {total_points}")

    lines.append("\n  " + "=" * 50)
    return "\n".join(lines)


def save_results_json(
    standings: List[PlayerStats],
    matches: List[MatchResult],
    output_path: Path,
) -> None:
    """
    Save results to JSON file.

    Args:
        standings: List of player statistics
        matches: List of match results
        output_path: Path to output file
    """
    data = {
        "standings": [
            {
                "player_id": s.player_id,
                "display_name": s.display_name,
                "strategy": s.strategy,
                "wins": s.wins,
                "draws": s.draws,
                "losses": s.losses,
                "points": s.points,
            }
            for s in standings
        ],
        "matches": [
            {
                "match_id": m.match_id,
                "round_num": m.round_num,
                "player_a": m.player_a,
                "player_b": m.player_b,
                "choice_a": m.choice_a,
                "choice_b": m.choice_b,
                "drawn_number": m.drawn_number,
                "winner": m.winner,
            }
            for m in matches
        ],
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def load_results_json(input_path: Path) -> tuple:
    """
    Load results from JSON file.

    Args:
        input_path: Path to input file

    Returns:
        Tuple of (standings, matches)
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    standings = [
        PlayerStats(**s) for s in data.get("standings", [])
    ]
    matches = [
        MatchResult(**m) for m in data.get("matches", [])
    ]

    return standings, matches
