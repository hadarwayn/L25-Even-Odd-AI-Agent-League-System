"""
Player P04 - DeltaBot with Adaptive strategy on port 8104.
"""

import sys
from pathlib import Path

# Add parent to path for template imports
template_dir = Path(__file__).parent.parent / "player_template"
sys.path.insert(0, str(template_dir))

from main import PlayerAgent


if __name__ == "__main__":
    player = PlayerAgent(
        player_id="P04",
        port=8104,
        display_name="DeltaBot",
        strategy_name="adaptive",
    )
    player.run()
