"""
Full League Simulation - Entry point for Even/Odd league.

Runs a complete league simulation with configurable execution mode.
Usage: python run_league.py [--parallel]
"""

import sys

from simulation import (
    LeagueSimulation,
    print_match_history,
    print_activity_log,
    print_final_results,
)


def main(parallel: bool = False) -> LeagueSimulation:
    """Run the full league simulation."""
    print("\n" + "="*80)
    mode = "PARALLEL" if parallel else "SEQUENTIAL"
    print(f"       EVEN/ODD AI AGENT LEAGUE - {mode} SIMULATION")
    print("="*80 + "\n")

    sim = LeagueSimulation(parallel=parallel)

    print("--- Registering Referees ---")
    sim.register_referee("REF01")
    sim.register_referee("REF02")

    print("\n--- Registering Players ---")
    sim.register_player("P01", "AlphaBot", "random")
    sim.register_player("P02", "BetaBot", "deterministic_even")
    sim.register_player("P03", "GammaBot", "alternating")
    sim.register_player("P04", "DeltaBot", "adaptive")

    print("\n--- Generating Schedule ---")
    sim.generate_schedule()

    print("\n--- Running League ---")
    sim.run_league()

    print_match_history(sim.match_results)
    print_activity_log(sim.activity_log)
    print_final_results(sim.get_standings(), sim.get_performance_stats())

    return sim


if __name__ == "__main__":
    parallel_mode = "--parallel" in sys.argv
    main(parallel=parallel_mode)
