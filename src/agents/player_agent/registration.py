"""
Registration client for the Player Agent.

Handles initial registration with the League Manager.
"""

from typing import Optional
import httpx

from .state import PlayerState
from ...protocol.messages import (
    create_register_request,
    parse_register_response,
    RegistrationStatus,
    get_utc_timestamp,
    generate_conversation_id,
)
from ...utils.config import Config, get_contact_endpoint
from ...utils.logger import JsonLogger
from ...utils.resilience import retry_with_backoff, RetryExhausted


class RegistrationError(Exception):
    """Raised when registration fails."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Registration failed: {reason}")


async def register_with_league(
    config: Config,
    state: PlayerState,
    logger: JsonLogger,
) -> bool:
    """
    Register the player agent with the League Manager.

    Args:
        config: Agent configuration
        state: Player state manager
        logger: JSON logger

    Returns:
        True if registration successful

    Raises:
        RegistrationError: If registration is rejected
        RetryExhausted: If all connection attempts fail
    """
    contact_endpoint = get_contact_endpoint(config)

    # Build registration request
    request_payload = create_register_request(
        display_name=config.agent.display_name,
        contact_endpoint=contact_endpoint,
        version=config.agent.version,
        protocol_version=config.agent.protocol_version,
        game_types=config.agent.game_types,
    )

    logger.info(
        "REGISTRATION_START",
        f"Registering with League Manager at {config.league_manager.endpoint}",
        display_name=config.agent.display_name,
        contact_endpoint=contact_endpoint,
    )

    # Build JSON-RPC request
    jsonrpc_request = {
        "jsonrpc": "2.0",
        "method": "league_register",
        "params": request_payload,
        "id": 1,
    }

    async def _do_register() -> dict:
        async with httpx.AsyncClient(timeout=config.timeouts.registration) as client:
            response = await client.post(
                config.league_manager.endpoint,
                json=jsonrpc_request,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    try:
        response_data = await retry_with_backoff(
            _do_register,
            max_retries=config.retry.max_retries,
            backoff_seconds=config.retry.backoff_seconds,
            retryable_exceptions=(httpx.TimeoutException, httpx.ConnectError),
        )
    except RetryExhausted as e:
        logger.error(
            "REGISTRATION_FAILED",
            f"Failed to connect to League Manager after {e.attempts} attempts",
            error=str(e.last_error),
        )
        raise

    # Parse response
    result = response_data.get("result", {})

    if not result:
        # Try params directly (some implementations use params)
        result = response_data.get("params", response_data)

    try:
        reg_response = parse_register_response(result)
    except Exception as e:
        logger.error(
            "REGISTRATION_PARSE_ERROR",
            f"Failed to parse registration response: {e}",
        )
        raise RegistrationError(f"Invalid response format: {e}")

    # Check registration status
    if reg_response.status == RegistrationStatus.REJECTED:
        reason = reg_response.reason or "Unknown reason"
        logger.error(
            "REGISTRATION_REJECTED",
            f"Registration rejected: {reason}",
        )
        raise RegistrationError(reason)

    # Registration successful - update state
    state.register(
        player_id=reg_response.player_id,
        auth_token=reg_response.auth_token,
        league_id=reg_response.league_id,
    )

    logger.info(
        "REGISTRATION_SUCCESS",
        f"Successfully registered as {reg_response.player_id}",
        player_id=reg_response.player_id,
        league_id=reg_response.league_id,
    )

    return True
