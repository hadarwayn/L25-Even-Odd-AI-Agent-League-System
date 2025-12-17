"""
Unit tests for sender string parsing.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.helpers import parse_sender, format_sender, determine_parity


class TestSenderParsing:
    """Tests for sender string parsing."""

    def test_parse_player_sender(self):
        """Parse player sender string."""
        agent_type, agent_id = parse_sender("player:P01")
        assert agent_type == "player"
        assert agent_id == "P01"

    def test_parse_referee_sender(self):
        """Parse referee sender string."""
        agent_type, agent_id = parse_sender("referee:REF01")
        assert agent_type == "referee"
        assert agent_id == "REF01"

    def test_format_sender(self):
        """Format sender string."""
        sender = format_sender("player", "P01")
        assert sender == "player:P01"

    def test_invalid_sender_raises(self):
        """Invalid sender format raises ValueError."""
        with pytest.raises(ValueError):
            parse_sender("invalid_sender")


class TestParityDetermination:
    """Tests for parity determination."""

    def test_determine_parity_even(self):
        """Even numbers identified correctly."""
        assert determine_parity(2) == "even"
        assert determine_parity(0) == "even"
        assert determine_parity(100) == "even"

    def test_determine_parity_odd(self):
        """Odd numbers identified correctly."""
        assert determine_parity(1) == "odd"
        assert determine_parity(3) == "odd"
        assert determine_parity(99) == "odd"
