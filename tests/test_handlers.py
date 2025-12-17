"""
Unit tests for message handlers.

Tests the handler classes for handling:
- Game invitations
- Parity choice calls
- Game over messages
- Error messages
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Add SHARED and agents to path
sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))
sys.path.insert(0, str(Path(__file__).parent.parent / "agents"))

from league_sdk.helpers import utc_now, generate_uuid
from league_sdk.game_rules.even_odd import EvenOddGame, determine_winner


class TestEvenOddGameLogic:
    """Tests for Even/Odd game logic."""

    def test_get_parity_even(self):
        """Even numbers return 'even'."""
        game = EvenOddGame()
        assert game.get_parity(2) == "even"
        assert game.get_parity(4) == "even"
        assert game.get_parity(10) == "even"

    def test_get_parity_odd(self):
        """Odd numbers return 'odd'."""
        game = EvenOddGame()
        assert game.get_parity(1) == "odd"
        assert game.get_parity(3) == "odd"
        assert game.get_parity(9) == "odd"

    def test_draw_number_in_range(self):
        """Drawn number is within specified range."""
        game = EvenOddGame(min_number=1, max_number=10)
        for _ in range(100):
            num = game.draw_number()
            assert 1 <= num <= 10

    def test_both_correct_is_draw(self):
        """Both players correct results in draw."""
        game = EvenOddGame()
        outcome = game.determine_match_outcome(
            "P01", "even",
            "P02", "even",
            drawn_number=4,  # Even number
        )
        assert outcome.player_a_result == "DRAW"
        assert outcome.player_b_result == "DRAW"
        assert outcome.winner_id is None

    def test_both_wrong_is_draw(self):
        """Both players wrong results in draw."""
        game = EvenOddGame()
        outcome = game.determine_match_outcome(
            "P01", "odd",
            "P02", "odd",
            drawn_number=4,  # Even number, both chose odd
        )
        assert outcome.player_a_result == "DRAW"
        assert outcome.player_b_result == "DRAW"
        assert outcome.winner_id is None

    def test_player_a_wins(self):
        """Player A wins when only A is correct."""
        game = EvenOddGame()
        outcome = game.determine_match_outcome(
            "P01", "even",
            "P02", "odd",
            drawn_number=4,  # Even number
        )
        assert outcome.player_a_result == "WIN"
        assert outcome.player_b_result == "LOSS"
        assert outcome.winner_id == "P01"

    def test_player_b_wins(self):
        """Player B wins when only B is correct."""
        game = EvenOddGame()
        outcome = game.determine_match_outcome(
            "P01", "even",
            "P02", "odd",
            drawn_number=3,  # Odd number
        )
        assert outcome.player_a_result == "LOSS"
        assert outcome.player_b_result == "WIN"
        assert outcome.winner_id == "P02"

    def test_determine_winner_convenience_function(self):
        """Test convenience function for determining winner."""
        result_a, result_b, winner = determine_winner("even", "odd", 4)
        assert result_a == "WIN"
        assert result_b == "LOSS"
        assert winner == "player_a"


class TestPointsCalculation:
    """Tests for points calculation."""

    def test_win_points(self):
        """Win awards 3 points."""
        from league_sdk.helpers import calculate_points
        assert calculate_points("WIN") == 3

    def test_draw_points(self):
        """Draw awards 1 point."""
        from league_sdk.helpers import calculate_points
        assert calculate_points("DRAW") == 1

    def test_loss_points(self):
        """Loss awards 0 points."""
        from league_sdk.helpers import calculate_points
        assert calculate_points("LOSS") == 0

    def test_technical_loss_points(self):
        """Technical loss awards 0 points."""
        from league_sdk.helpers import calculate_points
        assert calculate_points("TECHNICAL_LOSS") == 0


class TestSenderParsing:
    """Tests for sender string parsing."""

    def test_parse_player_sender(self):
        """Parse player sender string."""
        from league_sdk.helpers import parse_sender
        agent_type, agent_id = parse_sender("player:P01")
        assert agent_type == "player"
        assert agent_id == "P01"

    def test_parse_referee_sender(self):
        """Parse referee sender string."""
        from league_sdk.helpers import parse_sender
        agent_type, agent_id = parse_sender("referee:REF01")
        assert agent_type == "referee"
        assert agent_id == "REF01"

    def test_format_sender(self):
        """Format sender string."""
        from league_sdk.helpers import format_sender
        sender = format_sender("player", "P01")
        assert sender == "player:P01"

    def test_invalid_sender_raises(self):
        """Invalid sender format raises ValueError."""
        from league_sdk.helpers import parse_sender
        with pytest.raises(ValueError):
            parse_sender("invalid_sender")


class TestParityDetermination:
    """Tests for parity determination."""

    def test_determine_parity_even(self):
        """Even numbers identified correctly."""
        from league_sdk.helpers import determine_parity
        assert determine_parity(2) == "even"
        assert determine_parity(0) == "even"
        assert determine_parity(100) == "even"

    def test_determine_parity_odd(self):
        """Odd numbers identified correctly."""
        from league_sdk.helpers import determine_parity
        assert determine_parity(1) == "odd"
        assert determine_parity(3) == "odd"
        assert determine_parity(99) == "odd"
