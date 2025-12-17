"""
Message handlers for the Player Agent.

Handles all incoming MCP messages and generates appropriate responses.
"""

from typing import Any, Optional

from .state import PlayerState
from ...protocol.messages import (
    GameInvitation,
    GameJoinAck,
    ChooseParityCall,
    ChooseParityResponse,
    GameOver,
    LeagueStandingsUpdate,
    RoundAnnouncement,
    RoundCompleted,
    LeagueCompleted,
    LeagueError,
    GameError,
    ParityChoice,
    create_envelope,
    get_utc_timestamp,
)
from ...strategy.base import BaseStrategy
from ...utils.logger import JsonLogger


class MessageHandler:
    """
    Handles incoming MCP messages for the Player Agent.

    Routes messages to appropriate handler methods and generates responses.
    """

    def __init__(
        self,
        state: PlayerState,
        strategy: BaseStrategy,
        logger: JsonLogger,
    ):
        """
        Initialize the message handler.

        Args:
            state: Player state manager
            strategy: Parity choice strategy
            logger: JSON logger
        """
        self.state = state
        self.strategy = strategy
        self.logger = logger

        # Message type to handler mapping
        self._handlers = {
            "game_invitation": self._handle_game_invitation,
            "GAME_INVITATION": self._handle_game_invitation,
            "choose_parity_call": self._handle_choose_parity,
            "CHOOSE_PARITY_CALL": self._handle_choose_parity,
            "game_over": self._handle_game_over,
            "GAME_OVER": self._handle_game_over,
            "league_standings_update": self._handle_standings,
            "LEAGUE_STANDINGS_UPDATE": self._handle_standings,
            "round_announcement": self._handle_round_announcement,
            "ROUND_ANNOUNCEMENT": self._handle_round_announcement,
            "round_completed": self._handle_round_completed,
            "ROUND_COMPLETED": self._handle_round_completed,
            "league_completed": self._handle_league_completed,
            "LEAGUE_COMPLETED": self._handle_league_completed,
            "league_error": self._handle_league_error,
            "LEAGUE_ERROR": self._handle_league_error,
            "game_error": self._handle_game_error,
            "GAME_ERROR": self._handle_game_error,
        }

    async def handle_message(
        self,
        method: str,
        params: dict[str, Any],
    ) -> Optional[dict[str, Any]]:
        """
        Route and handle an incoming message.

        Args:
            method: Message type/method name
            params: Message payload

        Returns:
            Response payload or None for notifications
        """
        handler = self._handlers.get(method)

        if handler:
            return await handler(params)
        else:
            self.logger.warning(
                "UNKNOWN_MESSAGE",
                f"Unknown message type: {method}",
                method=method,
            )
            return None

    async def _handle_game_invitation(self, params: dict) -> dict:
        """Handle GAME_INVITATION message."""
        try:
            invitation = GameInvitation.model_validate(params)
        except Exception as e:
            self.logger.error("INVITATION_PARSE_ERROR", f"Failed to parse invitation: {e}")
            raise

        # Extract details
        details = invitation.game_invitation
        match_id = invitation.match_id
        opponent_id = details.opponent_id
        role = details.role_in_match.value

        self.logger.info(
            "GAME_INVITATION",
            f"Received invitation for match {match_id} vs {opponent_id}",
            match_id=match_id,
            opponent_id=opponent_id,
            role=role,
        )

        # Update state
        self.state.start_match(
            match_id=match_id,
            round_id=invitation.round_id,
            opponent_id=opponent_id,
            role=role,
            conversation_id=invitation.conversation_id,
        )

        # Build GAME_JOIN_ACK response
        response = {
            "protocol": "league.v2",
            "message_type": "GAME_JOIN_ACK",
            "sender": f"player:{self.state.player_id}",
            "timestamp": get_utc_timestamp(),
            "conversation_id": invitation.conversation_id,
            "auth_token": self.state.auth_token,
            "league_id": invitation.league_id,
            "round_id": invitation.round_id,
            "match_id": match_id,
            "accept": True,
        }

        self.logger.log_message_sent(
            message_type="GAME_JOIN_ACK",
            recipient=invitation.sender,
            match_id=match_id,
        )

        return response

    async def _handle_choose_parity(self, params: dict) -> dict:
        """Handle CHOOSE_PARITY_CALL message."""
        try:
            call = ChooseParityCall.model_validate(params)
        except Exception as e:
            self.logger.error("PARITY_CALL_PARSE_ERROR", f"Failed to parse parity call: {e}")
            raise

        match_id = call.match_id
        opponent_id = call.parity_context.opponent_id
        standings = call.parity_context.your_standings

        self.logger.info(
            "CHOOSE_PARITY_CALL",
            f"Choosing parity for match {match_id}",
            match_id=match_id,
            deadline=call.deadline,
        )

        # Use strategy to choose parity
        choice = self.strategy.choose_parity(
            opponent_id=opponent_id,
            my_standings=standings,
        )

        # Record the choice
        self.state.record_choice(choice)

        self.logger.info(
            "PARITY_CHOICE",
            f"Chose '{choice}' for match {match_id}",
            match_id=match_id,
            choice=choice,
        )

        # Build CHOOSE_PARITY_RESPONSE
        response = {
            "protocol": "league.v2",
            "message_type": "CHOOSE_PARITY_RESPONSE",
            "sender": f"player:{self.state.player_id}",
            "timestamp": get_utc_timestamp(),
            "conversation_id": call.conversation_id,
            "auth_token": self.state.auth_token,
            "league_id": call.league_id,
            "round_id": call.round_id,
            "match_id": match_id,
            "player_id": self.state.player_id,
            "parity_choice": choice,
        }

        self.logger.log_message_sent(
            message_type="CHOOSE_PARITY_RESPONSE",
            recipient=call.sender,
            match_id=match_id,
        )

        return response

    async def _handle_game_over(self, params: dict) -> dict:
        """Handle GAME_OVER message."""
        try:
            game_over = GameOver.model_validate(params)
        except Exception as e:
            self.logger.error("GAME_OVER_PARSE_ERROR", f"Failed to parse game over: {e}")
            raise

        result = game_over.game_result
        match_id = game_over.match_id

        # Determine our result
        if result.winner_player_id == self.state.player_id:
            our_result = "WIN"
        elif result.status.value == "DRAW":
            our_result = "DRAW"
        else:
            our_result = "LOSS"

        # Get our choice from the result
        our_choice = result.choices.get(self.state.player_id, "unknown")

        self.logger.log_game_result(
            match_id=match_id,
            result=our_result,
            choice=our_choice,
            drawn_number=result.drawn_number,
            opponent_id=self.state.current_match.opponent_id if self.state.current_match else "unknown",
        )

        # Update state
        self.state.end_match(our_result)

        return {"status": "acknowledged", "match_id": match_id}

    async def _handle_standings(self, params: dict) -> dict:
        """Handle LEAGUE_STANDINGS_UPDATE message."""
        try:
            standings = LeagueStandingsUpdate.model_validate(params)
        except Exception as e:
            self.logger.warning("STANDINGS_PARSE_ERROR", f"Failed to parse standings: {e}")
            return {"status": "acknowledged"}

        # Find our rank
        our_rank = None
        for entry in standings.standings:
            if entry.player_id == self.state.player_id:
                our_rank = entry.rank
                break

        self.logger.info(
            "STANDINGS_UPDATE",
            f"Received standings update, our rank: {our_rank}",
            round_id=standings.round_id,
            rank=our_rank,
        )

        return {"status": "acknowledged"}

    async def _handle_round_announcement(self, params: dict) -> dict:
        """Handle ROUND_ANNOUNCEMENT message."""
        self.logger.info(
            "ROUND_ANNOUNCEMENT",
            f"Round announcement received",
            round_id=params.get("round_id"),
        )
        return {"status": "acknowledged"}

    async def _handle_round_completed(self, params: dict) -> dict:
        """Handle ROUND_COMPLETED message."""
        self.logger.info(
            "ROUND_COMPLETED",
            f"Round {params.get('round_id')} completed",
            round_id=params.get("round_id"),
        )
        return {"status": "acknowledged"}

    async def _handle_league_completed(self, params: dict) -> dict:
        """Handle LEAGUE_COMPLETED message."""
        self.logger.info(
            "LEAGUE_COMPLETED",
            "League has completed",
            league_id=params.get("league_id"),
        )
        self.state.shutdown()
        return {"status": "acknowledged"}

    async def _handle_league_error(self, params: dict) -> dict:
        """Handle LEAGUE_ERROR message."""
        self.logger.error(
            "LEAGUE_ERROR",
            f"League error: {params.get('error_name')} - {params.get('error_description')}",
            error_code=params.get("error_code"),
            retryable=params.get("retryable", False),
        )
        return {"status": "acknowledged"}

    async def _handle_game_error(self, params: dict) -> dict:
        """Handle GAME_ERROR message."""
        self.logger.error(
            "GAME_ERROR",
            f"Game error: {params.get('error_name')} - {params.get('error_description')}",
            error_code=params.get("error_code"),
            match_id=params.get("match_id"),
            retryable=params.get("retryable", False),
        )
        return {"status": "acknowledged"}
