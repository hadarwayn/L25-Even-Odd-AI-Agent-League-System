"""
Unit tests for helper functions.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.helpers import utc_now, generate_uuid


class TestHelperFunctions:
    """Tests for utility functions."""

    def test_utc_now_format(self):
        """Generated timestamp has correct format."""
        ts = utc_now()
        assert ts.endswith("Z")
        assert "T" in ts

    def test_generate_uuid_uniqueness(self):
        """Generated UUIDs are unique."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2

    def test_generate_uuid_format(self):
        """Generated UUID has correct format."""
        uuid = generate_uuid()
        assert len(uuid) == 36  # Standard UUID format
        assert uuid.count("-") == 4
