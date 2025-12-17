"""
Message handlers for the Referee agent.
"""

from typing import TYPE_CHECKING

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from league_sdk import utc_now

if TYPE_CHECKING:
    from main import RefereeAgent


class RefereeHandlers:
    """Message handlers for Referee agent."""

    def __init__(self, referee: "RefereeAgent"):
        """Initialize handlers."""
        self.referee = referee
        self.logger = referee.logger

    async def handle_game_join_ack(self, params: dict) -> dict:
        """Handle player's game join acknowledgment."""
        match_id = params.get("match_id")
        sender = params.get("sender", "")
        status = params.get("status", "ACCEPTED")

        if status != "ACCEPTED":
            self.logger.warning(
                "JOIN_DECLINED",
                f"Player declined match {match_id}",
                sender=sender,
            )
            return {"status": "RECEIVED"}

        # Update match state
        match_state = self.referee.active_matches.get(match_id)
        if not match_state:
            self.logger.warning("UNKNOWN_MATCH", f"Unknown match {match_id}")
            return {"status": "ERROR", "message": "Unknown match"}

        # Determine which player joined
        player_id = sender.split(":")[-1] if ":" in sender else sender

        if match_state["player_a"]["id"] == player_id:
            match_state["player_a_joined"] = True
        elif match_state["player_b"]["id"] == player_id:
            match_state["player_b_joined"] = True

        self.logger.info(
            "PLAYER_JOINED",
            f"Player {player_id} joined match {match_id}",
            match_id=match_id,
        )

        return {"status": "RECEIVED"}

    async def handle_parity_response(self, params: dict) -> dict:
        """Handle player's parity choice response."""
        match_id = params.get("match_id")
        sender = params.get("sender", "")
        parity_choice = params.get("parity_choice")

        # Validate choice
        if parity_choice not in ("even", "odd"):
            self.logger.error(
                "INVALID_CHOICE",
                f"Invalid parity choice: {parity_choice}",
                match_id=match_id,
            )
            return {"status": "ERROR", "message": "Invalid parity choice"}

        # Update match state
        match_state = self.referee.active_matches.get(match_id)
        if not match_state:
            self.logger.warning("UNKNOWN_MATCH", f"Unknown match {match_id}")
            return {"status": "ERROR", "message": "Unknown match"}

        # Record choice
        player_id = sender.split(":")[-1] if ":" in sender else sender

        if match_state["player_a"]["id"] == player_id:
            match_state["player_a_choice"] = parity_choice
        elif match_state["player_b"]["id"] == player_id:
            match_state["player_b_choice"] = parity_choice

        self.logger.info(
            "CHOICE_RECEIVED",
            f"Player {player_id} chose {parity_choice}",
            match_id=match_id,
        )

        return {"status": "RECEIVED"}

    async def handle_match_assignment(self, params: dict) -> dict:
        """Handle match assignment from League Manager."""
        match_id = params.get("match_id")
        round_id = params.get("round_id")
        player_a_id = params.get("player_a")
        player_b_id = params.get("player_b")
        player_a_endpoint = params.get("player_a_endpoint")
        player_b_endpoint = params.get("player_b_endpoint")

        self.logger.info(
            "MATCH_ASSIGNED",
            f"Assigned match {match_id}: {player_a_id} vs {player_b_id}",
            match_id=match_id,
        )

        # Start match orchestration
        player_a = {"id": player_a_id, "endpoint": player_a_endpoint}
        player_b = {"id": player_b_id, "endpoint": player_b_endpoint}

        result = await self.referee.orchestrator.conduct_match(
            match_id, round_id, player_a, player_b
        )

        # Report result to manager
        await self._report_result(result)

        return {"status": "COMPLETED", "result": result}

    async def _report_result(self, result: dict) -> None:
        """Report match result to League Manager."""
        from league_sdk import MCPClient

        manager_endpoint = self.referee.config.agents.get("league_manager", {}).get(
            "endpoint", "http://127.0.0.1:8000/mcp"
        )

        client = MCPClient(
            f"referee:{self.referee.referee_id}",
            self.referee.auth_token,
        )

        try:
            await client.send(
                manager_endpoint,
                "MATCH_RESULT_REPORT",
                {
                    "match_id": result.get("match_id"),
                    "round_id": result.get("round_id"),
                    "player_a_id": result.get("player_a", {}).get("id"),
                    "player_b_id": result.get("player_b", {}).get("id"),
                    "player_a_choice": result.get("player_a_choice"),
                    "player_b_choice": result.get("player_b_choice"),
                    "drawn_number": result.get("drawn_number"),
                    "winner_id": result.get("winner_id"),
                    "player_a_result": result.get("player_a_result"),
                    "player_b_result": result.get("player_b_result"),
                },
            )
            self.logger.info("RESULT_REPORTED", f"Reported match {result.get('match_id')}")
        except Exception as e:
            self.logger.error("REPORT_FAILED", str(e))
        finally:
            await client.close()
