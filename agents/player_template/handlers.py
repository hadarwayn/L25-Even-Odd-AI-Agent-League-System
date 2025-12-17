"""
Message handlers for the Player agent.
"""

from typing import TYPE_CHECKING

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from league_sdk import MCPClient, utc_now

if TYPE_CHECKING:
    from main import PlayerAgent


class PlayerHandlers:
    """Message handlers for Player agent."""

    def __init__(self, player: "PlayerAgent"):
        """Initialize handlers."""
        self.player = player
        self.logger = player.logger

    async def handle_game_invitation(self, params: dict) -> dict:
        """Handle game invitation from referee."""
        match_id = params.get("match_id")
        opponent_id = params.get("opponent_id")
        role = params.get("role_in_match")
        referee_sender = params.get("sender", "")

        self.logger.info(
            "INVITATION_RECEIVED",
            f"Match {match_id} vs {opponent_id} as {role}",
            match_id=match_id,
        )

        # Update state
        self.player.state.set_active(match_id, opponent_id)

        # Send acknowledgment
        return self.player.server.build_response(
            "GAME_JOIN_ACK",
            conversation_id=params.get("conversation_id"),
            match_id=match_id,
            status="ACCEPTED",
        )

    async def handle_choose_parity(self, params: dict) -> dict:
        """Handle parity choice request."""
        match_id = params.get("match_id")
        opponent_id = self.player.state.current_opponent_id

        # Use strategy to choose
        choice = self.player.strategy.choose(
            match_id,
            opponent_id,
            self.player.state.history,
        )

        self.logger.info(
            "CHOICE_MADE",
            f"Chose {choice} for match {match_id}",
            match_id=match_id,
            choice=choice,
        )

        return self.player.server.build_response(
            "CHOOSE_PARITY_RESPONSE",
            conversation_id=params.get("conversation_id"),
            match_id=match_id,
            parity_choice=choice,
        )

    async def handle_game_over(self, params: dict) -> dict:
        """Handle game over notification."""
        match_id = params.get("match_id")
        result = params.get("result")
        drawn_number = params.get("drawn_number")
        your_choice = params.get("your_choice")
        opponent_choice = params.get("opponent_choice")
        points_earned = params.get("points_earned", 0)

        self.logger.info(
            "GAME_OVER",
            f"Match {match_id}: {result} (drew {drawn_number})",
            match_id=match_id,
            result=result,
        )

        # Record result
        match_data = {
            "match_id": match_id,
            "result": result,
            "choice": your_choice,
            "opponent_choice": opponent_choice,
            "drawn_number": drawn_number,
            "points_earned": points_earned,
        }
        self.player.state.record_result(result, match_data)

        # Update strategy
        self.player.strategy.update({
            "opponent_id": self.player.state.current_opponent_id,
            "opponent_choice": opponent_choice,
            "result": result,
        })

        return {"status": "RECEIVED"}

    async def handle_round_announcement(self, params: dict) -> dict:
        """Handle round announcement."""
        round_id = params.get("round_id")
        round_number = params.get("round_number")
        matches = params.get("matches", [])

        self.logger.info(
            "ROUND_ANNOUNCED",
            f"Round {round_number} starting with {len(matches)} matches",
            round_id=round_id,
        )

        return {"status": "RECEIVED"}

    async def handle_standings_update(self, params: dict) -> dict:
        """Handle standings update."""
        standings = params.get("standings", [])

        # Find our position
        player_id = self.player.state.assigned_id or self.player.player_id
        our_standing = next(
            (s for s in standings if s.get("player_id") == player_id),
            None,
        )

        if our_standing:
            self.logger.info(
                "STANDINGS_UPDATE",
                f"Rank {our_standing.get('rank')}: {our_standing.get('points')} pts",
            )

        return {"status": "RECEIVED"}

    async def handle_league_completed(self, params: dict) -> dict:
        """Handle league completion."""
        final_standings = params.get("final_standings", [])

        # Find final position
        player_id = self.player.state.assigned_id or self.player.player_id
        our_standing = next(
            (s for s in final_standings if s.get("player_id") == player_id),
            None,
        )

        if our_standing:
            self.logger.info(
                "LEAGUE_COMPLETED",
                f"Final rank: {our_standing.get('rank')} with {our_standing.get('points')} pts",
            )

        return {"status": "RECEIVED"}
