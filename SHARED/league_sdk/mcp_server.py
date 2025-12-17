"""
Base MCP server class for agents.

Provides FastAPI-based MCP server foundation with authentication
and rate limiting support.
"""

from typing import Any, Callable, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from .helpers import utc_now, generate_uuid, validate_utc
from .logger import JsonLogger
from .auth import (
    RateLimiter,
    AuthTokenValidator,
    requires_auth,
    sanitize_metadata,
)


class MCPServer:
    """Base MCP server for agents with auth and rate limiting."""

    def __init__(
        self,
        agent_type: str,
        agent_id: str,
        host: str = "127.0.0.1",
        port: int = 8000,
        enable_rate_limiting: bool = True,
        rate_limit: int = 100,
    ):
        """
        Initialize MCP server.

        Args:
            agent_type: Type of agent (league_manager, referee, player)
            agent_id: Agent identifier
            host: Server host
            port: Server port
            enable_rate_limiting: Whether to enable rate limiting
            rate_limit: Max requests per minute per sender
        """
        self.agent_type = agent_type
        self.agent_id = agent_id
        self.host = host
        self.port = port
        self.sender = f"{agent_type}:{agent_id}"

        self.app = FastAPI(title=f"{agent_type.title()} {agent_id}")
        self.logger = JsonLogger(agent_type, agent_id)
        self._handlers: dict[str, Callable] = {}

        # Security components
        self._rate_limiter = RateLimiter(max_requests=rate_limit)
        self._auth_validator = AuthTokenValidator()
        self._enable_rate_limiting = enable_rate_limiting

        self._setup_routes()

    def _setup_routes(self) -> None:
        """Setup FastAPI routes."""

        @self.app.post("/mcp")
        async def mcp_endpoint(request: Request) -> JSONResponse:
            return await self._handle_request(request)

        @self.app.get("/health")
        async def health() -> dict[str, str]:
            return {"status": "healthy", "agent": self.sender}

    async def _handle_request(self, request: Request) -> JSONResponse:
        """Handle incoming MCP request with auth and rate limiting."""
        try:
            body = await request.json()
        except Exception:
            return self._error_response(None, -32700, "Parse error")

        # Validate JSON-RPC structure
        if body.get("jsonrpc") != "2.0":
            return self._error_response(body.get("id"), -32600, "Invalid Request")

        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")
        sender = params.get("sender", "unknown")

        # Rate limiting check
        if self._enable_rate_limiting and not self._rate_limiter.is_allowed(sender):
            self.logger.warning("RATE_LIMITED", f"Rate limit exceeded: {sender}")
            return self._error_response(request_id, -32000, "Rate limit exceeded")

        # Validate envelope
        if not self._validate_envelope(params):
            return self._error_response(request_id, -32602, "Invalid envelope")

        # Auth token validation for protected messages
        if requires_auth(method):
            auth_token = params.get("auth_token")
            if not self._validate_auth_token(auth_token, params):
                self.logger.warning("AUTH_FAILED", f"Invalid auth: {sender}")
                return self._error_response(request_id, -32001, "Auth failed")

        # Log incoming message
        self.logger.message_received(method, sender)

        # Route to handler
        handler = self._handlers.get(method)
        if not handler:
            return self._error_response(request_id, -32601, f"Unknown: {method}")

        try:
            result = await handler(params)
            return JSONResponse({
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id,
            })
        except Exception as e:
            self.logger.error("HANDLER_ERROR", str(e), method=method)
            return self._error_response(request_id, -32603, str(e))

    def _validate_envelope(self, params: dict[str, Any]) -> bool:
        """Validate message envelope."""
        required = ["protocol", "message_type", "sender", "timestamp", "conversation_id"]
        if not all(k in params for k in required):
            return False
        if params.get("protocol") != "league.v2":
            return False
        if not validate_utc(params.get("timestamp", "")):
            return False
        return True

    def _validate_auth_token(self, token: Optional[str], params: dict) -> bool:
        """Validate auth token for request."""
        if not token:
            return False
        return self._auth_validator.validate_token(token)

    def register_auth_token(self, agent_id: str, token: str) -> None:
        """Register a valid auth token for an agent."""
        self._auth_validator.register_token(agent_id, token)

    def _error_response(
        self,
        request_id: Optional[str],
        code: int,
        message: str,
    ) -> JSONResponse:
        """Create JSON-RPC error response."""
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": code, "message": message},
            "id": request_id,
        })

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Register a message handler."""
        self._handlers[message_type] = handler

    def build_response(self, message_type: str, **kwargs: Any) -> dict[str, Any]:
        """Build a response envelope."""
        return {
            "protocol": "league.v2",
            "message_type": message_type,
            "sender": self.sender,
            "timestamp": utc_now(),
            "conversation_id": kwargs.pop("conversation_id", generate_uuid()),
            **kwargs,
        }
