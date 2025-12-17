"""
Unit tests for points calculation.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.helpers import calculate_points


class TestPointsCalculation:
    """Tests for points calculation."""

    def test_win_points(self):
        """Win awards 3 points."""
        assert calculate_points("WIN") == 3

    def test_draw_points(self):
        """Draw awards 1 point."""
        assert calculate_points("DRAW") == 1

    def test_loss_points(self):
        """Loss awards 0 points."""
        assert calculate_points("LOSS") == 0

    def test_technical_loss_points(self):
        """Technical loss awards 0 points."""
        assert calculate_points("TECHNICAL_LOSS") == 0
