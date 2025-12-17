"""
LLM-based strategy for parity choice.

Uses an LLM to make game decisions based on history and context.
"""

import os
from typing import Optional, Literal

from .base import BaseStrategy, ParityChoice


class LLMStrategy(BaseStrategy):
    """Strategy that uses an LLM for decision making."""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Initialize LLM strategy.

        Args:
            model: LLM model identifier
            temperature: Sampling temperature (0.0-1.0)
        """
        self.model = model
        self.temperature = temperature
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self._client = None

    @property
    def name(self) -> str:
        """Strategy name."""
        return f"llm-{self.model}"

    def _get_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except ImportError:
                return None
        return self._client

    def choose(
        self,
        match_id: str,
        opponent_id: str,
        history: Optional[list[dict]] = None,
    ) -> ParityChoice:
        """
        Use LLM to choose parity.

        Falls back to random if LLM unavailable.
        """
        client = self._get_client()
        if not client or not self.api_key:
            # Fallback to random choice
            import random
            return random.choice(["even", "odd"])

        # Build context from history
        history_text = self._format_history(history, opponent_id)

        prompt = f"""You are playing an Even/Odd guessing game.
A random number will be drawn, and you must guess if it's even or odd.

{history_text}

Match: {match_id}
Opponent: {opponent_id}

Respond with ONLY "even" or "odd" - nothing else."""

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=10,
            )
            choice = response.choices[0].message.content.strip().lower()
            if choice in ("even", "odd"):
                return choice
        except Exception:
            pass

        # Fallback
        import random
        return random.choice(["even", "odd"])

    def _format_history(
        self,
        history: Optional[list[dict]],
        opponent_id: str,
    ) -> str:
        """Format game history for LLM context."""
        if not history:
            return "No previous games against this opponent."

        opponent_games = [
            g for g in history
            if g.get("opponent_id") == opponent_id
        ]

        if not opponent_games:
            return "No previous games against this opponent."

        lines = ["Previous games against this opponent:"]
        for game in opponent_games[-5:]:  # Last 5 games
            result = game.get("result", "?")
            your_choice = game.get("your_choice", "?")
            opp_choice = game.get("opponent_choice", "?")
            number = game.get("drawn_number", "?")
            lines.append(
                f"- You chose {your_choice}, opponent chose {opp_choice}, "
                f"number was {number} ({result})"
            )

        return "\n".join(lines)

    def update(self, result: dict) -> None:
        """Update is not needed for LLM strategy."""
        pass
