"""
Unit tests for message handlers.

Tests the MessageHandler class for handling:
- Game invitations
- Parity choice calls
- Game over messages
- Error messages
"""

import pytest
from unittest.mock import Mock, AsyncMock

from src.agents.player_agent.state import PlayerState, AgentLifecycle
from src.agents.player_agent.handlers import MessageHandler
from src.strategy.random_strategy import RandomStrategy


@pytest.fixture
def player_state():
    """Create a registered player state."""
    state = PlayerState()
    state.register(
        player_id="P01",
        auth_token="tok_test_abc123",
        league_id="league_2025",
    )
    return state


@pytest.fixture
def mock_logger():
    """Create a mock logger."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.log_message_received = Mock()
    logger.log_message_sent = Mock()
    logger.log_game_result = Mock()
    return logger


@pytest.fixture
def handler(player_state, mock_logger):
    """Create a message handler."""
    strategy = RandomStrategy(seed=42)  # Fixed seed for reproducibility
    return MessageHandler(
        state=player_state,
        strategy=strategy,
        logger=mock_logger,
    )


class TestGameInvitationHandler:
    """Tests for handling GAME_INVITATION messages."""

    @pytest.mark.asyncio
    async def test_accept_game_invitation(self, handler, player_state):
        """Handler accepts game invitation and returns GAME_JOIN_ACK."""
        invitation = {
            "protocol": "league.v2",
            "message_type": "GAME_INVITATION",
            "sender": "referee:REF01",
            "timestamp": "2025-01-15T10:30:00Z",
            "conversation_id": "conv-r1m1-001",
            "league_id": "league_2025",
            "round_id": 1,
            "match_id": "R1M1",
            "game_invitation": {
                "game_type": "even_odd",
                "match_id": "R1M1",
                "role_in_match": "PLAYER_A",
                "opponent_id": "P02",
            },
        }

        response = await handler.handle_message("GAME_INVITATION", invitation)

        assert response["message_type"] == "GAME_JOIN_ACK"
        assert response["accept"] is True
        assert response["match_id"] == "R1M1"
        assert response["auth_token"] == "tok_test_abc123"
        assert player_state.lifecycle == AgentLifecycle.ACTIVE

    @pytest.mark.asyncio
    async def test_invitation_updates_state(self, handler, player_state):
        """Game invitation updates player state with match info."""
        invitation = {
            "protocol": "league.v2",
            "message_type": "GAME_INVITATION",
            "sender": "referee:REF01",
            "timestamp": "2025-01-15T10:30:00Z",
            "conversation_id": "conv-r1m1-001",
            "league_id": "league_2025",
            "round_id": 1,
            "match_id": "R1M1",
            "game_invitation": {
                "game_type": "even_odd",
                "match_id": "R1M1",
                "role_in_match": "PLAYER_B",
                "opponent_id": "P03",
            },
        }

        await handler.handle_message("GAME_INVITATION", invitation)

        assert player_state.current_match is not None
        assert player_state.current_match.match_id == "R1M1"
        assert player_state.current_match.opponent_id == "P03"
        assert player_state.current_match.role == "PLAYER_B"


class TestChooseParityHandler:
    """Tests for handling CHOOSE_PARITY_CALL messages."""

    @pytest.mark.asyncio
    async def test_choose_parity_returns_valid_choice(self, handler, player_state):
        """Handler returns valid parity choice."""
        # First accept an invitation
        invitation = {
            "protocol": "league.v2",
            "message_type": "GAME_INVITATION",
            "sender": "referee:REF01",
            "timestamp": "2025-01-15T10:30:00Z",
            "conversation_id": "conv-r1m1-001",
            "league_id": "league_2025",
            "round_id": 1,
            "match_id": "R1M1",
            "game_invitation": {
                "game_type": "even_odd",
                "match_id": "R1M1",
                "role_in_match": "PLAYER_A",
                "opponent_id": "P02",
            },
        }
        await handler.handle_message("GAME_INVITATION", invitation)

        parity_call = {
            "protocol": "league.v2",
            "message_type": "CHOOSE_PARITY_CALL",
            "sender": "referee:REF01",
            "timestamp": "2025-01-15T10:30:10Z",
            "conversation_id": "conv-r1m1-001",
            "league_id": "league_2025",
            "round_id": 1,
            "match_id": "R1M1",
            "player_id": "P01",
            "parity_context": {
                "valid_options": ["even", "odd"],
                "your_standings": {"wins": 0, "losses": 0, "draws": 0},
                "opponent_id": "P02",
            },
            "deadline": "2025-01-15T10:30:40Z",
        }

        response = await handler.handle_message("CHOOSE_PARITY_CALL", parity_call)

        assert response["message_type"] == "CHOOSE_PARITY_RESPONSE"
        assert response["parity_choice"] in ("even", "odd")
        assert response["auth_token"] == "tok_test_abc123"


class TestGameOverHandler:
    """Tests for handling GAME_OVER messages."""

    @pytest.mark.asyncio
    async def test_game_over_updates_stats(self, handler, player_state):
        """Game over updates player statistics."""
        # Setup match state
        player_state.start_match(
            match_id="R1M1",
            round_id=1,
            opponent_id="P02",
            role="PLAYER_A",
            conversation_id="conv-001",
        )
        player_state.record_choice("even")

        game_over = {
            "protocol": "league.v2",
            "message_type": "GAME_OVER",
            "sender": "referee:REF01",
            "timestamp": "2025-01-15T10:31:00Z",
            "conversation_id": "conv-001",
            "league_id": "league_2025",
            "round_id": 1,
            "match_id": "R1M1",
            "game_result": {
                "status": "WIN",
                "winner_player_id": "P01",
                "drawn_number": 8,
                "choices": {"P01": "even", "P02": "odd"},
            },
        }

        await handler.handle_message("GAME_OVER", game_over)

        assert player_state.stats.wins == 1
        assert player_state.stats.total_games == 1
        assert player_state.current_match is None


class TestErrorHandlers:
    """Tests for error message handling."""

    @pytest.mark.asyncio
    async def test_league_error_logged(self, handler, mock_logger):
        """League error is logged without crashing."""
        error = {
            "protocol": "league.v2",
            "message_type": "LEAGUE_ERROR",
            "sender": "league_manager",
            "timestamp": "2025-01-15T10:35:00Z",
            "error_code": "E005",
            "error_name": "PLAYER_NOT_REGISTERED",
            "error_description": "Player ID not found",
            "retryable": False,
        }

        response = await handler.handle_message("LEAGUE_ERROR", error)

        assert response["status"] == "acknowledged"
        mock_logger.error.assert_called()

    @pytest.mark.asyncio
    async def test_game_error_logged(self, handler, mock_logger):
        """Game error is logged without crashing."""
        error = {
            "protocol": "league.v2",
            "message_type": "GAME_ERROR",
            "sender": "referee:REF01",
            "timestamp": "2025-01-15T10:31:00Z",
            "match_id": "R1M1",
            "player_id": "P01",
            "error_code": "E001",
            "error_name": "TIMEOUT_ERROR",
            "error_description": "Response not received in time",
            "retryable": True,
        }

        response = await handler.handle_message("GAME_ERROR", error)

        assert response["status"] == "acknowledged"
        mock_logger.error.assert_called()
