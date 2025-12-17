"""
Unit tests for protocol models.

Tests Pydantic models for:
- Message envelope validation
- UTC timestamp validation
- Registration messages
- Game messages
- Error codes
"""

import pytest
from pydantic import ValidationError

from src.protocol.envelope import MessageEnvelope, get_utc_timestamp, create_envelope
from src.protocol.registration import (
    PlayerMeta,
    LeagueRegisterRequest,
    LeagueRegisterResponse,
    RegistrationStatus,
    create_register_request,
)
from src.protocol.game_messages import (
    ParityChoice,
    RoleInMatch,
    GameResultStatus,
    ChooseParityResponse,
)
from src.protocol.errors import ErrorCode, is_retryable


class TestMessageEnvelope:
    """Tests for MessageEnvelope validation."""

    def test_valid_envelope_with_z_timestamp(self):
        """Valid envelope with Z suffix timestamp."""
        envelope = MessageEnvelope(
            message_type="TEST",
            sender="player:P01",
            timestamp="2025-01-15T10:30:00Z",
            conversation_id="conv-001",
        )
        assert envelope.protocol == "league.v2"
        assert envelope.timestamp == "2025-01-15T10:30:00Z"

    def test_valid_envelope_with_offset_timestamp(self):
        """Valid envelope with +00:00 offset."""
        envelope = MessageEnvelope(
            message_type="TEST",
            sender="player:P01",
            timestamp="2025-01-15T10:30:00+00:00",
            conversation_id="conv-001",
        )
        assert envelope.timestamp == "2025-01-15T10:30:00+00:00"

    def test_invalid_timestamp_no_timezone(self):
        """Reject timestamp without timezone."""
        with pytest.raises(ValidationError) as exc_info:
            MessageEnvelope(
                message_type="TEST",
                sender="player:P01",
                timestamp="2025-01-15T10:30:00",
                conversation_id="conv-001",
            )
        assert "UTC" in str(exc_info.value)

    def test_invalid_timestamp_non_utc(self):
        """Reject timestamp with non-UTC timezone."""
        with pytest.raises(ValidationError) as exc_info:
            MessageEnvelope(
                message_type="TEST",
                sender="player:P01",
                timestamp="2025-01-15T10:30:00+02:00",
                conversation_id="conv-001",
            )
        assert "UTC" in str(exc_info.value)

    def test_valid_sender_player(self):
        """Valid player sender format."""
        envelope = MessageEnvelope(
            message_type="TEST",
            sender="player:P01",
            timestamp="2025-01-15T10:30:00Z",
            conversation_id="conv-001",
        )
        assert envelope.sender == "player:P01"

    def test_valid_sender_referee(self):
        """Valid referee sender format."""
        envelope = MessageEnvelope(
            message_type="TEST",
            sender="referee:REF01",
            timestamp="2025-01-15T10:30:00Z",
            conversation_id="conv-001",
        )
        assert envelope.sender == "referee:REF01"

    def test_valid_sender_league_manager(self):
        """Valid league_manager sender."""
        envelope = MessageEnvelope(
            message_type="TEST",
            sender="league_manager",
            timestamp="2025-01-15T10:30:00Z",
            conversation_id="conv-001",
        )
        assert envelope.sender == "league_manager"

    def test_invalid_sender_format(self):
        """Reject invalid sender format."""
        with pytest.raises(ValidationError):
            MessageEnvelope(
                message_type="TEST",
                sender="invalid_sender",
                timestamp="2025-01-15T10:30:00Z",
                conversation_id="conv-001",
            )


class TestParityChoice:
    """Tests for parity choice validation."""

    def test_valid_even(self):
        """Accept 'even' choice."""
        assert ParityChoice("even") == ParityChoice.EVEN

    def test_valid_odd(self):
        """Accept 'odd' choice."""
        assert ParityChoice("odd") == ParityChoice.ODD

    def test_invalid_choice(self):
        """Reject invalid parity choice."""
        with pytest.raises(ValueError):
            ParityChoice("neither")


class TestGameResultStatus:
    """Tests for game result status."""

    def test_win_status(self):
        """WIN status is valid."""
        assert GameResultStatus("WIN") == GameResultStatus.WIN

    def test_draw_status(self):
        """DRAW status is valid."""
        assert GameResultStatus("DRAW") == GameResultStatus.DRAW

    def test_technical_loss_status(self):
        """TECHNICAL_LOSS status is valid."""
        assert GameResultStatus("TECHNICAL_LOSS") == GameResultStatus.TECHNICAL_LOSS


class TestErrorCodes:
    """Tests for error codes."""

    def test_timeout_is_retryable(self):
        """E001 TIMEOUT_ERROR should be retryable."""
        assert is_retryable("E001") is True

    def test_connection_is_retryable(self):
        """E009 CONNECTION_ERROR should be retryable."""
        assert is_retryable("E009") is True

    def test_auth_not_retryable(self):
        """E011 AUTH_TOKEN_MISSING should not be retryable."""
        assert is_retryable("E011") is False

    def test_invalid_parity_not_retryable(self):
        """E004 INVALID_PARITY_CHOICE should not be retryable."""
        assert is_retryable("E004") is False


class TestRegistration:
    """Tests for registration messages."""

    def test_create_register_request(self):
        """Create valid registration request."""
        request = create_register_request(
            display_name="TestAgent",
            contact_endpoint="http://localhost:8101/mcp",
        )

        assert request["message_type"] == "LEAGUE_REGISTER_REQUEST"
        assert request["sender"] == "player:UNREGISTERED"
        assert request["player_meta"]["display_name"] == "TestAgent"
        assert "even_odd" in request["player_meta"]["game_types"]

    def test_registration_response_accepted(self):
        """Parse accepted registration response."""
        response = LeagueRegisterResponse(
            timestamp="2025-01-15T10:30:00Z",
            conversation_id="conv-001",
            status=RegistrationStatus.ACCEPTED,
            player_id="P01",
            auth_token="tok_abc123",
            league_id="league_2025",
        )

        assert response.status == RegistrationStatus.ACCEPTED
        assert response.player_id == "P01"
        assert response.auth_token == "tok_abc123"

    def test_registration_response_rejected(self):
        """Parse rejected registration response."""
        response = LeagueRegisterResponse(
            timestamp="2025-01-15T10:30:00Z",
            conversation_id="conv-001",
            status=RegistrationStatus.REJECTED,
            reason="League is full",
        )

        assert response.status == RegistrationStatus.REJECTED
        assert response.reason == "League is full"


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_get_utc_timestamp_format(self):
        """Generated timestamp has correct format."""
        ts = get_utc_timestamp()
        assert ts.endswith("Z")
        assert "T" in ts

    def test_create_envelope_sets_timestamp(self):
        """create_envelope sets current timestamp."""
        envelope = create_envelope(
            message_type="TEST",
            sender="player:P01",
        )
        assert envelope.timestamp.endswith("Z")
        assert envelope.conversation_id is not None
