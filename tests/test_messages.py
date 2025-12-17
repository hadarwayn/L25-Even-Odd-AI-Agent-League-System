"""
Unit tests for protocol message models.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "SHARED"))

from league_sdk.schemas_base import MessageEnvelope, PlayerMeta
from league_sdk.schemas import (
    LeagueRegisterRequest,
    LeagueRegisterResponse,
    ChooseParityResponse,
    GameOver,
)
from league_sdk.helpers import utc_now, generate_uuid


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
            sender="manager:MANAGER",
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
            sender="manager:MANAGER",
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
