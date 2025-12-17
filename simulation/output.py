"""
Output formatting functions for league simulation.
"""

from typing import List, Dict, Any


def print_standings(standings: List[Dict[str, Any]], title: str = "Standings") -> None:
    """Print standings table."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(f"  {'Rank':<6}{'Player':<12}{'Strategy':<20}{'P':>4}{'W':>4}{'D':>4}{'L':>4}{'Pts':>5}")
    print(f"  {'-'*60}")
    for s in standings:
        print(f"  {s['rank']:<6}{s['player_id']:<12}{s['strategy']:<20}"
              f"{s['played']:>4}{s['wins']:>4}{s['draws']:>4}{s['losses']:>4}{s['points']:>5}")
    print(f"{'='*70}\n")


def print_match_history(match_results: List[Dict[str, Any]]) -> None:
    """Print all match results."""
    print(f"\n{'='*80}")
    print("  MATCH HISTORY")
    print(f"{'='*80}")
    print(f"  {'Match':<8}{'Round':<7}{'Player A':<10}{'Choice':<8}{'vs':<4}"
          f"{'Player B':<10}{'Choice':<8}{'Draw#':<6}{'Winner':<8}")
    print(f"  {'-'*75}")
    for m in match_results:
        winner = m['winner'] if m['winner'] else 'DRAW'
        print(f"  {m['match_id']:<8}{m['round_num']:<7}{m['player_a']:<10}{m['choice_a']:<8}"
              f"{'vs':<4}{m['player_b']:<10}{m['choice_b']:<8}{m['drawn_number']:<6}{winner:<8}")
    print(f"{'='*80}\n")


def print_activity_log(activity_log: List[Dict[str, Any]]) -> None:
    """Print activity log."""
    print(f"\n{'='*80}")
    print("  LEAGUE ACTIVITY LOG")
    print(f"{'='*80}")
    print(f"  {'Time':<12}{'Event':<25}{'Details':<40}")
    print(f"  {'-'*75}")
    for entry in activity_log:
        time_str = entry['timestamp'][11:19]
        print(f"  {time_str:<12}{entry['event']:<25}{entry['message']:<40}")
    print(f"{'='*80}\n")


def print_final_results(
    standings: List[Dict[str, Any]],
    stats: Dict[str, Any],
) -> None:
    """Print final results with champion info."""
    print("\n" + "="*80)
    print("       FINAL RESULTS")
    print("="*80)
    print_standings(standings, "FINAL STANDINGS")

    winner = standings[0]
    print(f"\n  CHAMPION: {winner['player_id']} ({winner['display_name']})")
    print(f"  Strategy: {winner['strategy']}")
    print(f"  Record: {winner['wins']}W-{winner['draws']}D-{winner['losses']}L ({winner['points']} points)")

    if stats:
        print(f"\n  PERFORMANCE: {stats['total_duration_ms']:.2f}ms total, "
              f"{stats['avg_match_time_ms']:.2f}ms/match")

    print("\n" + "="*80 + "\n")
