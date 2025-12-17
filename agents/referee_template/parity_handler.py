"""
Parity choice handling for the Referee.

Handles collecting parity choices and determining winners.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from league_sdk import MCPClient
from league_sdk.game_rules import EvenOddGame

if TYPE_CHECKING:
    from main import RefereeAgent


class ParityHandler:
    """Handles parity choice collection and winner determination."""

    def __init__(self, referee: "RefereeAgent"):
        """Initialize handler."""
        self.referee = referee
        self.logger = referee.logger
        self.game = EvenOddGame()

    async def request_parity_choices(self, match_state: dict) -> bool:
        """
        Request parity choices from both players.

        Returns:
            True if both players responded within deadline
        """
        match_id = match_state["match_id"]
        deadline = (datetime.now(timezone.utc) + timedelta(seconds=30)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        client = MCPClient(
            f"referee:{self.referee.referee_id}",
            self.referee.auth_token,
        )

        async def request_choice(player: dict) -> bool:
            try:
                await client.send(
                    player["endpoint"],
                    "CHOOSE_PARITY_CALL",
                    {"match_id": match_id, "deadline": deadline},
                )
                return True
            except Exception as e:
                self.logger.error("CHOICE_REQUEST_FAILED", str(e))
                return False

        tasks = [
            request_choice(match_state["player_a"]),
            request_choice(match_state["player_b"]),
        ]

        await asyncio.gather(*tasks)
        await client.close()

        # Wait for choices
        await asyncio.sleep(30)

        return (
            match_state["player_a_choice"] is not None
            and match_state["player_b_choice"] is not None
        )

    def determine_winner(self, match_state: dict) -> dict:
        """Determine match winner based on parity choices."""
        outcome = self.game.determine_match_outcome(
            match_state["player_a"]["id"],
            match_state["player_a_choice"],
            match_state["player_b"]["id"],
            match_state["player_b_choice"],
        )

        self.logger.match_event(
            match_state["match_id"],
            f"Result: {outcome.winner_id or 'DRAW'}",
        )

        return {
            "match_id": match_state["match_id"],
            "round_id": match_state["round_id"],
            "drawn_number": outcome.drawn_number,
            "player_a_choice": outcome.player_a_choice,
            "player_b_choice": outcome.player_b_choice,
            "player_a_result": outcome.player_a_result,
            "player_b_result": outcome.player_b_result,
            "winner_id": outcome.winner_id,
        }
