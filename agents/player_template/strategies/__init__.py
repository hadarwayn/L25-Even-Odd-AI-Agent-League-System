"""
Player strategy implementations.
"""

from .base import BaseStrategy
from .random_strategy import RandomStrategy
from .deterministic import DeterministicEvenStrategy, DeterministicOddStrategy
from .alternating import AlternatingStrategy
from .adaptive import AdaptiveStrategy
from .llm_strategy import LLMStrategy

__all__ = [
    "BaseStrategy",
    "RandomStrategy",
    "DeterministicEvenStrategy",
    "DeterministicOddStrategy",
    "AlternatingStrategy",
    "AdaptiveStrategy",
    "LLMStrategy",
]


def get_strategy(name: str) -> BaseStrategy:
    """Get strategy by name."""
    strategies = {
        "random": RandomStrategy,
        "deterministic_even": DeterministicEvenStrategy,
        "deterministic_odd": DeterministicOddStrategy,
        "alternating": AlternatingStrategy,
        "adaptive": AdaptiveStrategy,
        "llm": LLMStrategy,
    }
    strategy_class = strategies.get(name, RandomStrategy)
    return strategy_class()
