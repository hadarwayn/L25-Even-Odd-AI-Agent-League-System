"""
Unit tests for UTC timestamp validation.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.helpers import validate_utc


class TestUTCTimestampValidation:
    """Tests for UTC timestamp validation."""

    def test_valid_timestamp_with_z_suffix(self):
        """Valid timestamp with Z suffix."""
        assert validate_utc("2025-01-15T10:30:00Z") is True

    def test_valid_timestamp_with_utc_offset(self):
        """Valid timestamp with +00:00 offset."""
        assert validate_utc("2025-01-15T10:30:00+00:00") is True

    def test_invalid_timestamp_no_timezone(self):
        """Reject timestamp without timezone."""
        assert validate_utc("2025-01-15T10:30:00") is False

    def test_invalid_timestamp_non_utc(self):
        """Reject timestamp with non-UTC timezone."""
        assert validate_utc("2025-01-15T10:30:00+02:00") is False

    def test_empty_timestamp(self):
        """Reject empty timestamp."""
        assert validate_utc("") is False

    def test_none_timestamp(self):
        """Reject None timestamp."""
        assert validate_utc(None) is False
