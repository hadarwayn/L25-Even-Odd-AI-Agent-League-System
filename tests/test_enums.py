"""
Unit tests for protocol enums.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.schemas_base import ParityChoice, GameResult
from league_sdk.helpers import is_retryable_error


class TestParityChoice:
    """Tests for parity choice validation."""

    def test_valid_even(self):
        """Accept 'even' choice."""
        assert ParityChoice("even") == "even"

    def test_valid_odd(self):
        """Accept 'odd' choice."""
        assert ParityChoice("odd") == "odd"


class TestGameResult:
    """Tests for game result status."""

    def test_win_status(self):
        """WIN status is valid."""
        assert GameResult("WIN") == "WIN"

    def test_draw_status(self):
        """DRAW status is valid."""
        assert GameResult("DRAW") == "DRAW"

    def test_loss_status(self):
        """LOSS status is valid."""
        assert GameResult("LOSS") == "LOSS"

    def test_technical_loss_status(self):
        """TECHNICAL_LOSS status is valid."""
        assert GameResult("TECHNICAL_LOSS") == "TECHNICAL_LOSS"


class TestErrorCodes:
    """Tests for error codes."""

    def test_timeout_is_retryable(self):
        """E001 TIMEOUT_ERROR should be retryable."""
        assert is_retryable_error("E001") is True

    def test_connection_is_retryable(self):
        """E009 CONNECTION_ERROR should be retryable."""
        assert is_retryable_error("E009") is True

    def test_auth_not_retryable(self):
        """E011 AUTH_TOKEN_MISSING should not be retryable."""
        assert is_retryable_error("E011") is False

    def test_invalid_parity_not_retryable(self):
        """E004 INVALID_PARITY_CHOICE should not be retryable."""
        assert is_retryable_error("E004") is False
