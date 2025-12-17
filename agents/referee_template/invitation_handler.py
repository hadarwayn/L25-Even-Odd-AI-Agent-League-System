"""
Game invitation handling for the Referee.

Handles sending game invitations to players.
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import TYPE_CHECKING

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from league_sdk import MCPClient

if TYPE_CHECKING:
    from main import RefereeAgent


class InvitationHandler:
    """Handles game invitations."""

    def __init__(self, referee: "RefereeAgent"):
        """Initialize handler."""
        self.referee = referee
        self.logger = referee.logger

    async def send_invitations(self, match_state: dict) -> bool:
        """
        Send game invitations to both players.

        Returns:
            True if both players joined within deadline
        """
        match_id = match_state["match_id"]
        deadline = (datetime.now(timezone.utc) + timedelta(seconds=5)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )

        client = MCPClient(
            f"referee:{self.referee.referee_id}",
            self.referee.auth_token,
        )

        async def invite_player(player: dict, role: str, opponent_id: str) -> bool:
            try:
                await client.send(
                    player["endpoint"],
                    "GAME_INVITATION",
                    {
                        "match_id": match_id,
                        "round_id": match_state["round_id"],
                        "opponent_id": opponent_id,
                        "role_in_match": role,
                        "response_deadline": deadline,
                    },
                )
                return True
            except Exception as e:
                self.logger.error("INVITATION_FAILED", str(e), player_id=player["id"])
                return False

        # Send invitations in parallel
        tasks = [
            invite_player(
                match_state["player_a"],
                "PLAYER_A",
                match_state["player_b"]["id"],
            ),
            invite_player(
                match_state["player_b"],
                "PLAYER_B",
                match_state["player_a"]["id"],
            ),
        ]

        await asyncio.gather(*tasks)
        await client.close()

        # Wait for join acknowledgments
        await asyncio.sleep(5)

        return match_state["player_a_joined"] and match_state["player_b_joined"]
