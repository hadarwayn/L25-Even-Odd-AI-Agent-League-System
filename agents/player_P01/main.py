"""
Player P01 - AlphaBot with Random strategy on port 8101.
"""

import sys
from pathlib import Path

# Add parent to path for template imports
template_dir = Path(__file__).parent.parent / "player_template"
sys.path.insert(0, str(template_dir))

from main import PlayerAgent


if __name__ == "__main__":
    player = PlayerAgent(
        player_id="P01",
        port=8101,
        display_name="AlphaBot",
        strategy_name="random",
    )
    player.run()
