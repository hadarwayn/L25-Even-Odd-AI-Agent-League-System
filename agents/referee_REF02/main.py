"""
Referee REF02 - Instance on port 8002.
"""

import sys
from pathlib import Path

# Add parent to path for template imports
template_dir = Path(__file__).parent.parent / "referee_template"
sys.path.insert(0, str(template_dir))

from main import RefereeAgent


if __name__ == "__main__":
    referee = RefereeAgent("REF02", 8002)
    referee.run()
