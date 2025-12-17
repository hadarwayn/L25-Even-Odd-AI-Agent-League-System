"""
Unit tests for Even/Odd game logic.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

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
            drawn_number=4,
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
            drawn_number=4,
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
            drawn_number=4,
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
            drawn_number=3,
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
