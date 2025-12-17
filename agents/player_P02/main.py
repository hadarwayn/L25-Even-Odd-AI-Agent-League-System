"""
Player P02 - BetaBot with Deterministic Even strategy on port 8102.
"""

import sys
from pathlib import Path

# Add parent to path for template imports
template_dir = Path(__file__).parent.parent / "player_template"
sys.path.insert(0, str(template_dir))

from main import PlayerAgent


if __name__ == "__main__":
    player = PlayerAgent(
        player_id="P02",
        port=8102,
        display_name="BetaBot",
        strategy_name="deterministic_even",
    )
    player.run()
