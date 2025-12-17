"""
Async HTTP client for MCP communication.

Wraps httpx with retry logic and JSON-RPC formatting.
"""

from typing import Any, Optional
import httpx

from .resilience import retry_with_backoff, RetryExhausted, CircuitBreaker
from ..protocol.jsonrpc import create_jsonrpc_request


class McpClient:
    """
    HTTP client for MCP (Model Context Protocol) communication.

    Features:
    - Async requests with httpx
    - JSON-RPC 2.0 formatting
    - Retry with backoff for transient failures
    - Optional circuit breaker
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_seconds: float = 2.0,
        use_circuit_breaker: bool = False,
    ):
        """
        Initialize the MCP client.

        Args:
            base_url: Base URL for the MCP endpoint
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            backoff_seconds: Base backoff time
            use_circuit_breaker: Whether to use circuit breaker
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

        self._client: Optional[httpx.AsyncClient] = None
        self._circuit_breaker = CircuitBreaker() if use_circuit_breaker else None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def send_message(
        self,
        method: str,
        params: dict[str, Any],
        request_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Send a JSON-RPC message to the MCP endpoint.

        Args:
            method: The method name (message type in lowercase)
            params: The message payload
            request_id: Optional request ID

        Returns:
            Response data from the server

        Raises:
            RetryExhausted: If all retries fail
            httpx.HTTPError: For non-retryable HTTP errors
        """
        # Check circuit breaker
        if self._circuit_breaker and self._circuit_breaker.is_open():
            raise ConnectionError("Circuit breaker is open")

        # Build JSON-RPC request
        request_body = create_jsonrpc_request(method, params, request_id)

        async def _do_request() -> dict[str, Any]:
            client = await self._get_client()
            response = await client.post(
                self.base_url,
                json=request_body,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()

        try:
            result = await retry_with_backoff(
                _do_request,
                max_retries=self.max_retries,
                backoff_seconds=self.backoff_seconds,
                retryable_exceptions=(httpx.TimeoutException, httpx.ConnectError),
            )

            if self._circuit_breaker:
                self._circuit_breaker.record_success()

            return result

        except (RetryExhausted, httpx.HTTPError) as e:
            if self._circuit_breaker:
                self._circuit_breaker.record_failure()
            raise

    async def send_response(
        self,
        endpoint: str,
        method: str,
        params: dict[str, Any],
        request_id: Optional[int] = None,
    ) -> dict[str, Any]:
        """
        Send a JSON-RPC message to a specific endpoint.

        Args:
            endpoint: Full URL to send to
            method: The method name
            params: The message payload
            request_id: Optional request ID

        Returns:
            Response data from the server
        """
        request_body = create_jsonrpc_request(method, params, request_id)

        async def _do_request() -> dict[str, Any]:
            client = await self._get_client()
            response = await client.post(
                endpoint,
                json=request_body,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()

        return await retry_with_backoff(
            _do_request,
            max_retries=self.max_retries,
            backoff_seconds=self.backoff_seconds,
            retryable_exceptions=(httpx.TimeoutException, httpx.ConnectError),
        )


async def create_mcp_client(
    endpoint: str,
    timeout: float = 10.0,
    max_retries: int = 3,
) -> McpClient:
    """
    Create a configured MCP client.

    Args:
        endpoint: MCP endpoint URL
        timeout: Request timeout
        max_retries: Maximum retry attempts

    Returns:
        Configured McpClient instance
    """
    return McpClient(
        base_url=endpoint,
        timeout=timeout,
        max_retries=max_retries,
    )
