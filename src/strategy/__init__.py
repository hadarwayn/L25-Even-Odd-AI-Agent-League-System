"""
Strategy package.

Contains parity choice strategies for the Even/Odd game.
"""

from .base import BaseStrategy
from .random_strategy import RandomStrategy

__all__ = ["BaseStrategy", "RandomStrategy"]
