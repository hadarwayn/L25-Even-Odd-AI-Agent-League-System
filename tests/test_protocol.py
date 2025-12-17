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
import sys
from pathlib import Path

# Add SHARED to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.schemas_base import (
    MessageEnvelope,
    PlayerMeta,
    RefereeMeta,
    ParityChoice,
    GameResult,
    ErrorCode,
)
from league_sdk.schemas import (
    LeagueRegisterRequest,
    LeagueRegisterResponse,
    ChooseParityResponse,
    GameOver,
    LeagueError,
    GameError,
)
from league_sdk.helpers import (
    utc_now,
    generate_uuid,
    validate_utc,
    is_retryable_error,
)


class TestUTCTimestampValidation:
    """Tests for UTC timestamp validation."""

    def test_valid_timestamp_with_z_suffix(self):
        """Valid timestamp with Z suffix."""
        assert validate_utc("2025-01-15T10:30:00Z") is True

    def test_valid_timestamp_with_utc_offset(self):
        """Valid timestamp with +00:00 offset."""
        assert validate_utc("2025-01-15T10:30:00+00:00") is True

    def test_invalid_timestamp_no_timezone(self):
        """Reject timestamp without timezone."""
        assert validate_utc("2025-01-15T10:30:00") is False

    def test_invalid_timestamp_non_utc(self):
        """Reject timestamp with non-UTC timezone."""
        assert validate_utc("2025-01-15T10:30:00+02:00") is False

    def test_empty_timestamp(self):
        """Reject empty timestamp."""
        assert validate_utc("") is False

    def test_none_timestamp(self):
        """Reject None timestamp."""
        assert validate_utc(None) is False


class TestParityChoice:
    """Tests for parity choice validation."""

    def test_valid_even(self):
        """Accept 'even' choice."""
        assert ParityChoice("even") == "even"

    def test_valid_odd(self):
        """Accept 'odd' choice."""
        assert ParityChoice("odd") == "odd"


class TestGameResult:
    """Tests for game result status."""

    def test_win_status(self):
        """WIN status is valid."""
        assert GameResult("WIN") == "WIN"

    def test_draw_status(self):
        """DRAW status is valid."""
        assert GameResult("DRAW") == "DRAW"

    def test_loss_status(self):
        """LOSS status is valid."""
        assert GameResult("LOSS") == "LOSS"

    def test_technical_loss_status(self):
        """TECHNICAL_LOSS status is valid."""
        assert GameResult("TECHNICAL_LOSS") == "TECHNICAL_LOSS"


class TestErrorCodes:
    """Tests for error codes."""

    def test_timeout_is_retryable(self):
        """E001 TIMEOUT_ERROR should be retryable."""
        assert is_retryable_error("E001") is True

    def test_connection_is_retryable(self):
        """E009 CONNECTION_ERROR should be retryable."""
        assert is_retryable_error("E009") is True

    def test_auth_not_retryable(self):
        """E011 AUTH_TOKEN_MISSING should not be retryable."""
        assert is_retryable_error("E011") is False

    def test_invalid_parity_not_retryable(self):
        """E004 INVALID_PARITY_CHOICE should not be retryable."""
        assert is_retryable_error("E004") is False


class TestHelperFunctions:
    """Tests for utility functions."""

    def test_utc_now_format(self):
        """Generated timestamp has correct format."""
        ts = utc_now()
        assert ts.endswith("Z")
        assert "T" in ts

    def test_generate_uuid_uniqueness(self):
        """Generated UUIDs are unique."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()
        assert uuid1 != uuid2

    def test_generate_uuid_format(self):
        """Generated UUID has correct format."""
        uuid = generate_uuid()
        assert len(uuid) == 36  # Standard UUID format
        assert uuid.count("-") == 4


class TestMessageEnvelope:
    """Tests for message envelope creation."""

    def test_envelope_protocol_version(self):
        """Envelope has correct protocol version."""
        envelope = MessageEnvelope(
            message_type="TEST",
            sender="player:P01",
            timestamp=utc_now(),
            conversation_id=generate_uuid(),
        )
        assert envelope.protocol == "league.v2"

    def test_envelope_required_fields(self):
        """Envelope requires all mandatory fields."""
        envelope = MessageEnvelope(
            message_type="TEST",
            sender="player:P01",
            timestamp=utc_now(),
            conversation_id=generate_uuid(),
        )
        assert envelope.message_type == "TEST"
        assert envelope.sender == "player:P01"
        assert envelope.timestamp is not None
        assert envelope.conversation_id is not None


class TestRegistrationMessages:
    """Tests for registration message models."""

    def test_league_register_request(self):
        """Create valid registration request."""
        player_meta = PlayerMeta(
            display_name="TestAgent",
            contact_endpoint="http://localhost:8101/mcp",
        )
        request = LeagueRegisterRequest(
            sender="player:UNREGISTERED",
            timestamp=utc_now(),
            conversation_id=generate_uuid(),
            player_meta=player_meta,
        )
        assert request.message_type == "LEAGUE_REGISTER_REQUEST"
        assert request.player_meta.display_name == "TestAgent"

    def test_league_register_response_accepted(self):
        """Parse accepted registration response."""
        response = LeagueRegisterResponse(
            sender="league_manager",
            timestamp=utc_now(),
            conversation_id=generate_uuid(),
            status="REGISTERED",
            player_id="P01",
            auth_token="tok_abc123",
        )
        assert response.status == "REGISTERED"
        assert response.player_id == "P01"
        assert response.auth_token == "tok_abc123"

    def test_league_register_response_rejected(self):
        """Parse rejected registration response."""
        response = LeagueRegisterResponse(
            sender="league_manager",
            timestamp=utc_now(),
            conversation_id=generate_uuid(),
            status="REJECTED",
            reason="League is full",
        )
        assert response.status == "REJECTED"
        assert response.reason == "League is full"


class TestGameMessages:
    """Tests for game message models."""

    def test_choose_parity_response(self):
        """Create valid parity response."""
        response = ChooseParityResponse(
            sender="player:P01",
            timestamp=utc_now(),
            conversation_id=generate_uuid(),
            match_id="R1M1",
            parity_choice="even",
        )
        assert response.message_type == "CHOOSE_PARITY_RESPONSE"
        assert response.parity_choice == "even"

    def test_game_over_message(self):
        """Create valid game over message."""
        game_over = GameOver(
            sender="referee:REF01",
            timestamp=utc_now(),
            conversation_id=generate_uuid(),
            match_id="R1M1",
            drawn_number=7,
            your_choice="odd",
            opponent_choice="even",
            result="WIN",
            points_earned=3,
        )
        assert game_over.message_type == "GAME_OVER"
        assert game_over.result == "WIN"
        assert game_over.points_earned == 3
