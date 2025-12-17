"""
FastAPI MCP Server for the Player Agent.

Implements the HTTP endpoint for receiving MCP protocol messages
and routing them to appropriate handlers.
"""

from typing import Any, Optional
from fastapi import FastAPI, Request, Response
from pydantic import ValidationError
import json

from ..player_agent.state import PlayerState
from ..player_agent.handlers import MessageHandler
from ...protocol.jsonrpc import create_jsonrpc_response, create_error_response
from ...utils.logger import JsonLogger


def create_app(
    state: PlayerState,
    handler: MessageHandler,
    logger: JsonLogger,
) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        state: Player state manager
        handler: Message handler instance
        logger: JSON logger instance

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Player Agent MCP Server",
        description="MCP server for Even/Odd League Player Agent",
        version="1.0.0",
    )

    @app.post("/mcp")
    async def mcp_endpoint(request: Request) -> Response:
        """
        Main MCP endpoint for receiving JSON-RPC messages.

        Expects JSON-RPC 2.0 format:
        {
            "jsonrpc": "2.0",
            "method": "message_type",
            "params": { ... message payload ... },
            "id": <request_id>
        }
        """
        try:
            body = await request.json()
        except json.JSONDecodeError:
            logger.error("MCP_PARSE_ERROR", "Failed to parse JSON request body")
            return Response(
                content=json.dumps(
                    create_error_response(-32700, "Parse error", request_id=None)
                ),
                media_type="application/json",
                status_code=400,
            )

        # Extract JSON-RPC fields
        jsonrpc = body.get("jsonrpc", "2.0")
        method = body.get("method", "")
        params = body.get("params", {})
        request_id = body.get("id")

        if jsonrpc != "2.0":
            logger.warning("MCP_INVALID_VERSION", f"Invalid JSON-RPC version: {jsonrpc}")

        if not method:
            logger.error("MCP_NO_METHOD", "No method specified in request")
            return Response(
                content=json.dumps(
                    create_error_response(-32600, "Invalid Request: no method", request_id=request_id)
                ),
                media_type="application/json",
                status_code=400,
            )

        # Log received message
        message_type = params.get("message_type", method)
        sender = params.get("sender", "unknown")
        match_id = params.get("match_id")

        logger.log_message_received(
            message_type=message_type,
            sender=sender,
            match_id=match_id,
        )

        # Route to handler
        try:
            result = await handler.handle_message(method, params)

            # Build response
            if result is not None:
                response_data = create_jsonrpc_response(result=result, request_id=request_id)
            else:
                # Notification response (no result needed)
                response_data = create_jsonrpc_response(result={"status": "ok"}, request_id=request_id)

            return Response(
                content=json.dumps(response_data),
                media_type="application/json",
            )

        except ValidationError as e:
            logger.error("MCP_VALIDATION_ERROR", f"Validation error: {e}")
            return Response(
                content=json.dumps(
                    create_error_response(-32602, f"Invalid params: {e}", request_id=request_id)
                ),
                media_type="application/json",
                status_code=400,
            )

        except Exception as e:
            logger.error("MCP_HANDLER_ERROR", f"Handler error: {e}", error=str(e))
            return Response(
                content=json.dumps(
                    create_error_response(-32603, f"Internal error: {e}", request_id=request_id)
                ),
                media_type="application/json",
                status_code=500,
            )

    @app.get("/health")
    async def health_check() -> dict:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "player_id": state.player_id,
            "lifecycle": state.lifecycle.value,
            "registered": state.is_registered(),
        }

    @app.get("/stats")
    async def get_stats() -> dict:
        """Get player statistics."""
        return {
            "player_id": state.player_id,
            "wins": state.stats.wins,
            "losses": state.stats.losses,
            "draws": state.stats.draws,
            "total_games": state.stats.total_games,
        }

    return app
