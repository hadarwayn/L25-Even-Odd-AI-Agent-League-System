"""
Game orchestration logic for the Referee.

Handles match flow: invitation, parity collection, winner determination.
"""

import asyncio
from typing import TYPE_CHECKING, Optional
from datetime import datetime, timezone, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from league_sdk import MCPClient, utc_now, generate_uuid
from league_sdk.game_rules import EvenOddGame

if TYPE_CHECKING:
    from main import RefereeAgent


class GameOrchestrator:
    """Orchestrates match flow."""

    def __init__(self, referee: "RefereeAgent"):
        """Initialize orchestrator."""
        self.referee = referee
        self.logger = referee.logger
        self.game = EvenOddGame()

    async def conduct_match(
        self,
        match_id: str,
        round_id: str,
        player_a: dict,
        player_b: dict,
    ) -> dict:
        """
        Conduct a complete match.

        Args:
            match_id: Match identifier
            round_id: Round identifier
            player_a: Player A info with endpoint
            player_b: Player B info with endpoint

        Returns:
            Match result
        """
        self.logger.match_event(match_id, "Match starting")

        # Store match state
        match_state = {
            "match_id": match_id,
            "round_id": round_id,
            "player_a": player_a,
            "player_b": player_b,
            "player_a_joined": False,
            "player_b_joined": False,
            "player_a_choice": None,
            "player_b_choice": None,
        }
        self.referee.active_matches[match_id] = match_state

        try:
            # Step 1: Send invitations
            join_ok = await self._send_invitations(match_state)
            if not join_ok:
                return self._technical_loss_result(match_state, "join_timeout")

            # Step 2: Request parity choices
            choices_ok = await self._request_parity_choices(match_state)
            if not choices_ok:
                return self._technical_loss_result(match_state, "choice_timeout")

            # Step 3: Determine winner
            result = await self._determine_winner(match_state)

            # Step 4: Send game over to players
            await self._send_game_over(match_state, result)

            return result

        finally:
            # Cleanup
            self.referee.active_matches.pop(match_id, None)

    async def _send_invitations(self, match_state: dict) -> bool:
        """Send game invitations to both players."""
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

        results = await asyncio.gather(*tasks)
        await client.close()

        # Wait for join acknowledgments (simplified - actual would use events)
        await asyncio.sleep(5)

        return match_state["player_a_joined"] and match_state["player_b_joined"]

    async def _request_parity_choices(self, match_state: dict) -> bool:
        """Request parity choices from both players."""
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

    async def _determine_winner(self, match_state: dict) -> dict:
        """Determine match winner."""
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

    async def _send_game_over(self, match_state: dict, result: dict) -> None:
        """Send game over to both players."""
        # Implementation simplified for brevity
        self.logger.match_event(match_state["match_id"], "Match completed")

    def _technical_loss_result(self, match_state: dict, reason: str) -> dict:
        """Create technical loss result."""
        return {
            "match_id": match_state["match_id"],
            "round_id": match_state["round_id"],
            "error": reason,
            "player_a_result": "TECHNICAL_LOSS",
            "player_b_result": "TECHNICAL_LOSS",
        }
