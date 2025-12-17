"""
Message handlers for the League Manager.
"""

import asyncio
from typing import Any, TYPE_CHECKING

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "SHARED"))

from league_sdk import (
    utc_now,
    generate_uuid,
    generate_token,
    MCPClient,
)

if TYPE_CHECKING:
    from main import LeagueManager


class LeagueManagerHandlers:
    """Message handlers for League Manager."""

    def __init__(self, manager: "LeagueManager"):
        """Initialize handlers."""
        self.manager = manager
        self.logger = manager.logger

    async def handle_player_registration(self, params: dict) -> dict:
        """Handle player registration request."""
        player_meta = params.get("player_meta", {})
        display_name = player_meta.get("display_name", "Unknown")
        endpoint = player_meta.get("contact_endpoint")

        # Assign player ID
        self.manager.player_counter += 1
        player_id = f"P{self.manager.player_counter:02d}"
        auth_token = generate_token()

        # Store registration
        self.manager.registered_players[player_id] = {
            "player_id": player_id,
            "display_name": display_name,
            "endpoint": endpoint,
            "auth_token": auth_token,
            "meta": player_meta,
        }

        # Register in standings
        self.manager.standings.register_player(player_id, display_name)

        self.logger.info(
            "PLAYER_REGISTERED",
            f"Player {player_id} ({display_name}) registered",
            player_id=player_id,
        )

        # Check if we can start
        asyncio.create_task(self.manager.check_and_start_league())

        return self.manager.server.build_response(
            "LEAGUE_REGISTER_RESPONSE",
            conversation_id=params.get("conversation_id"),
            status="REGISTERED",
            player_id=player_id,
            auth_token=auth_token,
        )

    async def handle_referee_registration(self, params: dict) -> dict:
        """Handle referee registration request."""
        referee_meta = params.get("referee_meta", {})
        endpoint = referee_meta.get("contact_endpoint")

        # Assign referee ID
        self.manager.referee_counter += 1
        referee_id = f"REF{self.manager.referee_counter:02d}"
        auth_token = generate_token()

        # Store registration
        self.manager.registered_referees[referee_id] = {
            "referee_id": referee_id,
            "endpoint": endpoint,
            "auth_token": auth_token,
            "meta": referee_meta,
        }

        self.logger.info(
            "REFEREE_REGISTERED",
            f"Referee {referee_id} registered",
            referee_id=referee_id,
        )

        # Check if we can start
        asyncio.create_task(self.manager.check_and_start_league())

        return self.manager.server.build_response(
            "REFEREE_REGISTER_RESPONSE",
            conversation_id=params.get("conversation_id"),
            status="REGISTERED",
            referee_id=referee_id,
            auth_token=auth_token,
        )

    async def handle_match_result(self, params: dict) -> dict:
        """Handle match result report from referee."""
        match_id = params.get("match_id")
        player_a_id = params.get("player_a_id")
        player_b_id = params.get("player_b_id")
        player_a_result = params.get("player_a_result")
        player_b_result = params.get("player_b_result")

        # Update standings
        self.manager.standings.update_result(player_a_id, player_a_result)
        self.manager.standings.update_result(player_b_id, player_b_result)

        self.logger.match_event(
            match_id,
            f"Result: {player_a_id}={player_a_result}, {player_b_id}={player_b_result}",
        )

        # Broadcast standings
        await self.broadcast_standings()

        return {"status": "ACCEPTED"}

    async def handle_query(self, params: dict) -> dict:
        """Handle league query."""
        query_type = params.get("query_type")

        data = {}
        if query_type == "standings":
            data = {"standings": self.manager.standings.get_standings()}
        elif query_type == "schedule":
            data = self.manager.scheduler.get_schedule_summary()
        elif query_type == "stats":
            data = self.manager.standings.get_stats()
        elif query_type == "next_match":
            sender = params.get("sender", "")
            player_id = sender.split(":")[-1] if ":" in sender else None
            if player_id:
                data = {"match": self.manager.scheduler.get_player_next_match(player_id)}

        return self.manager.server.build_response(
            "LEAGUE_QUERY_RESPONSE",
            conversation_id=params.get("conversation_id"),
            query_type=query_type,
            data=data,
        )

    async def start_round(self) -> None:
        """Start a new round."""
        # Assign referees to matches
        referee_ids = list(self.manager.registered_referees.keys())
        self.manager.scheduler.assign_referees(referee_ids)

        round_matches = self.manager.scheduler.get_current_round()
        if not round_matches:
            await self.complete_league()
            return

        round_id = round_matches[0]["round_id"]
        round_num = self.manager.scheduler.current_round + 1

        self.logger.info("ROUND_START", f"Starting round {round_num}", round_id=round_id)

        # Broadcast round announcement
        await self.broadcast_round_announcement(round_id, round_num, round_matches)

        # Notify referees to start matches
        for match in round_matches:
            await self.notify_referee_start_match(match)

    async def broadcast_round_announcement(
        self, round_id: str, round_num: int, matches: list[dict]
    ) -> None:
        """Broadcast round announcement to all agents."""
        # Simplified: just log for now
        self.logger.info(
            "ROUND_ANNOUNCEMENT",
            f"Round {round_num} with {len(matches)} matches",
            round_id=round_id,
        )

    async def notify_referee_start_match(self, match: dict) -> None:
        """Notify referee to start a match."""
        referee_id = match.get("referee_id")
        referee = self.manager.registered_referees.get(referee_id)
        if not referee:
            return

        self.logger.info(
            "MATCH_ASSIGNED",
            f"Match {match['match_id']} assigned to {referee_id}",
            match_id=match["match_id"],
        )

    async def broadcast_standings(self) -> None:
        """Broadcast standings to all players."""
        standings = self.manager.standings.get_standings()
        self.logger.info("STANDINGS_UPDATE", f"Broadcasting standings to {len(standings)} players")

    async def complete_league(self) -> None:
        """Complete the league."""
        standings = self.manager.standings.get_standings()
        self.logger.info(
            "LEAGUE_COMPLETED",
            f"League completed. Winner: {standings[0]['player_id'] if standings else 'N/A'}",
        )
