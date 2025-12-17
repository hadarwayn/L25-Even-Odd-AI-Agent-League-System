"""
MCP HTTP client with retry logic, circuit breaker, and connection pooling.

Provides async HTTP client for inter-agent communication with resilience.
"""

import asyncio
from typing import Any, Optional
import httpx

from .helpers import utc_now, generate_uuid, is_retryable_error
from .circuit_breaker import CircuitBreaker, CircuitBreakerOpen, CircuitBreakerRegistry


# Configuration constants
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 2
DEFAULT_TIMEOUT_SECONDS = 30
DEFAULT_MAX_CONNECTIONS = 10


class MCPClient:
    """HTTP client for MCP protocol with circuit breaker and pooling."""

    _circuit_registry = CircuitBreakerRegistry()

    def __init__(
        self,
        sender: str,
        auth_token: Optional[str] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_seconds: int = DEFAULT_BACKOFF_SECONDS,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
        max_connections: int = DEFAULT_MAX_CONNECTIONS,
    ):
        """
        Initialize MCP client with connection pooling.

        Args:
            sender: Sender identifier (e.g., "player:P01")
            auth_token: Authentication token
            max_retries: Maximum retry attempts
            backoff_seconds: Seconds between retries
            timeout: Request timeout in seconds
            max_connections: Max keep-alive connections
        """
        self.sender = sender
        self.auth_token = auth_token
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.timeout = timeout
        self.max_connections = max_connections
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client with connection pooling."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.timeout,
                limits=httpx.Limits(
                    max_keepalive_connections=self.max_connections,
                    max_connections=self.max_connections * 2,
                ),
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    def _build_envelope(
        self,
        message_type: str,
        conversation_id: Optional[str] = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Build message envelope."""
        envelope = {
            "protocol": "league.v2",
            "message_type": message_type,
            "sender": self.sender,
            "timestamp": utc_now(),
            "conversation_id": conversation_id or generate_uuid(),
        }
        if self.auth_token:
            envelope["auth_token"] = self.auth_token
        envelope.update(kwargs)
        return envelope

    def _get_circuit_breaker(self, endpoint: str) -> CircuitBreaker:
        """Get circuit breaker for endpoint."""
        return self._circuit_registry.get(endpoint)

    async def send(
        self,
        endpoint: str,
        message_type: str,
        payload: dict[str, Any],
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send a message with retry logic and circuit breaker.

        Args:
            endpoint: Target endpoint URL
            message_type: Message type identifier
            payload: Message payload
            conversation_id: Optional conversation ID

        Returns:
            Response data
        """
        circuit = self._get_circuit_breaker(endpoint)

        if not circuit.can_execute():
            raise CircuitBreakerOpen(f"Circuit open for {endpoint}")

        envelope = self._build_envelope(message_type, conversation_id, **payload)

        jsonrpc_request = {
            "jsonrpc": "2.0",
            "method": message_type,
            "params": envelope,
            "id": generate_uuid(),
        }

        client = await self._get_client()
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                response = await client.post(
                    endpoint,
                    json=jsonrpc_request,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                circuit.record_success()
                return response.json()

            except httpx.TimeoutException as e:
                last_error = e
                circuit.record_failure()
                if attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_seconds * (attempt + 1))
                continue

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code >= 500:
                    circuit.record_failure()
                    if attempt < self.max_retries:
                        await asyncio.sleep(self.backoff_seconds * (attempt + 1))
                        continue
                raise

            except httpx.ConnectError as e:
                last_error = e
                circuit.record_failure()
                if attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_seconds * (attempt + 1))
                continue

        raise last_error or Exception("Max retries exceeded")

    def get_circuit_status(self) -> dict[str, dict]:
        """Get status of all circuit breakers."""
        return self._circuit_registry.get_all_status()

    def update_auth_token(self, token: str) -> None:
        """Update the auth token after registration."""
        self.auth_token = token
