"""
Player P03 - GammaBot with Alternating strategy on port 8103.
"""

import sys
from pathlib import Path

# Add parent to path for template imports
template_dir = Path(__file__).parent.parent / "player_template"
sys.path.insert(0, str(template_dir))

from main import PlayerAgent


if __name__ == "__main__":
    player = PlayerAgent(
        player_id="P03",
        port=8103,
        display_name="GammaBot",
        strategy_name="alternating",
    )
    player.run()
