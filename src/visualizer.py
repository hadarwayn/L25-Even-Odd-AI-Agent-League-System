"""
Visualizer for Player Agent statistics and results.

Generates graphs showing:
- Win/Loss/Draw distribution
- Game history timeline
- Strategy performance
"""

import json
from pathlib import Path
from typing import Optional
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server use


def load_history(history_path: str) -> list[dict]:
    """Load game history from JSON file."""
    path = Path(history_path)
    if not path.exists():
        return []

    with open(path, "r") as f:
        return json.load(f)


def create_results_pie_chart(
    wins: int,
    losses: int,
    draws: int,
    output_path: str,
    player_name: str = "Player Agent",
) -> None:
    """
    Create a pie chart showing game results distribution.

    Args:
        wins: Number of wins
        losses: Number of losses
        draws: Number of draws
        output_path: Path to save the chart
        player_name: Name for the chart title
    """
    fig, ax = plt.subplots(figsize=(10, 8))

    # Data
    sizes = [wins, losses, draws]
    labels = [f'Wins ({wins})', f'Losses ({losses})', f'Draws ({draws})']
    colors = ['#2ecc71', '#e74c3c', '#3498db']
    explode = (0.05, 0, 0)

    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 12}
    )

    # Title and styling
    ax.set_title(
        f'{player_name} - Game Results Distribution\n'
        f'Total Games: {wins + losses + draws}',
        fontsize=14,
        fontweight='bold',
        pad=20
    )

    # Add legend
    ax.legend(
        wedges,
        labels,
        title="Results",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"[OK] Pie chart saved to: {output_path}")


def create_game_timeline(
    history: list[dict],
    output_path: str,
    player_name: str = "Player Agent",
) -> None:
    """
    Create a timeline showing game results over time.

    Args:
        history: List of game records
        output_path: Path to save the chart
        player_name: Name for the chart title
    """
    if not history:
        print("[WARN] No game history to visualize")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    # Process data
    games = list(range(1, len(history) + 1))
    cumulative_wins = []
    cumulative_points = []

    wins = 0
    points = 0

    for game in history:
        result = game.get('result', 'LOSS')
        if result == 'WIN':
            wins += 1
            points += 3
        elif result == 'DRAW':
            points += 1
        cumulative_wins.append(wins)
        cumulative_points.append(points)

    # Plot
    ax.plot(games, cumulative_wins, 'g-o', label='Cumulative Wins', linewidth=2, markersize=8)
    ax.plot(games, cumulative_points, 'b-s', label='Cumulative Points', linewidth=2, markersize=8)

    # Styling
    ax.set_xlabel('Game Number', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title(
        f'{player_name} - Performance Over Time\n'
        f'{len(history)} Games Played',
        fontsize=14,
        fontweight='bold'
    )
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0.5, len(history) + 0.5)
    ax.set_ylim(0, max(cumulative_points) + 1 if cumulative_points else 10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"[OK] Timeline chart saved to: {output_path}")


def create_choice_distribution(
    history: list[dict],
    output_path: str,
    player_name: str = "Player Agent",
) -> None:
    """
    Create a bar chart showing choice distribution (even vs odd).

    Args:
        history: List of game records
        output_path: Path to save the chart
        player_name: Name for the chart title
    """
    if not history:
        print("[WARN] No game history to visualize")
        return

    fig, ax = plt.subplots(figsize=(10, 6))

    # Count choices and their outcomes
    even_wins = sum(1 for g in history if g.get('choice') == 'even' and g.get('result') == 'WIN')
    even_losses = sum(1 for g in history if g.get('choice') == 'even' and g.get('result') != 'WIN')
    odd_wins = sum(1 for g in history if g.get('choice') == 'odd' and g.get('result') == 'WIN')
    odd_losses = sum(1 for g in history if g.get('choice') == 'odd' and g.get('result') != 'WIN')

    # Data
    x = ['Even', 'Odd']
    wins = [even_wins, odd_wins]
    losses = [even_losses, odd_losses]

    x_pos = range(len(x))
    width = 0.35

    # Create bars
    bars1 = ax.bar([p - width/2 for p in x_pos], wins, width, label='Wins', color='#2ecc71')
    bars2 = ax.bar([p + width/2 for p in x_pos], losses, width, label='Losses/Draws', color='#e74c3c')

    # Add value labels on bars
    for bar in bars1 + bars2:
        height = bar.get_height()
        ax.annotate(f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')

    # Styling
    ax.set_xlabel('Choice', fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.set_title(
        f'{player_name} - Choice Performance Analysis',
        fontsize=14,
        fontweight='bold'
    )
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"[OK] Choice distribution chart saved to: {output_path}")


def generate_all_visualizations(
    player_id: str,
    data_dir: str = "data/players",
    results_dir: str = "results/graphs",
) -> None:
    """
    Generate all visualizations for a player.

    Args:
        player_id: Player identifier
        data_dir: Directory containing player data
        results_dir: Directory to save visualizations
    """
    # Ensure output directory exists
    Path(results_dir).mkdir(parents=True, exist_ok=True)

    # Load history
    history_path = Path(data_dir) / player_id / "history.json"
    history = load_history(str(history_path))

    # Calculate stats
    wins = sum(1 for g in history if g.get('result') == 'WIN')
    losses = sum(1 for g in history if g.get('result') in ('LOSS', 'TECHNICAL_LOSS'))
    draws = sum(1 for g in history if g.get('result') == 'DRAW')

    # Generate charts
    create_results_pie_chart(
        wins, losses, draws,
        f"{results_dir}/results_distribution.png",
        f"Player {player_id}"
    )

    create_game_timeline(
        history,
        f"{results_dir}/performance_timeline.png",
        f"Player {player_id}"
    )

    create_choice_distribution(
        history,
        f"{results_dir}/choice_analysis.png",
        f"Player {player_id}"
    )

    print(f"\n[OK] All visualizations generated in {results_dir}/")


if __name__ == "__main__":
    # Demo with sample data
    sample_history = [
        {"match_id": "R1M1", "choice": "even", "result": "WIN"},
        {"match_id": "R1M2", "choice": "odd", "result": "LOSS"},
        {"match_id": "R2M1", "choice": "even", "result": "WIN"},
        {"match_id": "R2M2", "choice": "odd", "result": "DRAW"},
        {"match_id": "R3M1", "choice": "even", "result": "WIN"},
    ]

    Path("results/graphs").mkdir(parents=True, exist_ok=True)

    create_results_pie_chart(3, 1, 1, "results/graphs/results_distribution.png")
    create_game_timeline(sample_history, "results/graphs/performance_timeline.png")
    create_choice_distribution(sample_history, "results/graphs/choice_analysis.png")
