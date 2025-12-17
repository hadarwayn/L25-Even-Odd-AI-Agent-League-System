"""
Unit tests for message handlers.

This module re-exports all handler tests from split modules.
Run with: pytest tests/test_handlers.py -v
"""

# Re-export all tests from split modules for backwards compatibility
from .test_game_logic import TestEvenOddGameLogic
from .test_points import TestPointsCalculation
from .test_sender import TestSenderParsing, TestParityDetermination

__all__ = [
    "TestEvenOddGameLogic",
    "TestPointsCalculation",
    "TestSenderParsing",
    "TestParityDetermination",
]
