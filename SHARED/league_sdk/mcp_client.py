"""
MCP HTTP client with retry logic.

Provides async HTTP client for inter-agent communication.
"""

import asyncio
from typing import Any, Optional
import httpx

from .helpers import utc_now, generate_uuid, is_retryable_error


class MCPClient:
    """HTTP client for MCP protocol communication."""

    def __init__(
        self,
        sender: str,
        auth_token: Optional[str] = None,
        max_retries: int = 3,
        backoff_seconds: int = 2,
        timeout: int = 30,
    ):
        """
        Initialize MCP client.

        Args:
            sender: Sender identifier (e.g., "player:P01")
            auth_token: Authentication token (required after registration)
            max_retries: Maximum retry attempts
            backoff_seconds: Seconds between retries
            timeout: Request timeout in seconds
        """
        self.sender = sender
        self.auth_token = auth_token
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
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

    async def send(
        self,
        endpoint: str,
        message_type: str,
        payload: dict[str, Any],
        conversation_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Send a message with retry logic.

        Args:
            endpoint: Target endpoint URL
            message_type: Message type identifier
            payload: Message payload
            conversation_id: Optional conversation ID

        Returns:
            Response data
        """
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
                return response.json()

            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_seconds)
                continue

            except httpx.HTTPStatusError as e:
                last_error = e
                if e.response.status_code >= 500 and attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_seconds)
                    continue
                raise

            except httpx.ConnectError as e:
                last_error = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.backoff_seconds)
                continue

        raise last_error or Exception("Max retries exceeded")
