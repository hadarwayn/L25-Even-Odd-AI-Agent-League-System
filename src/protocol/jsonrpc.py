"""
JSON-RPC 2.0 models for MCP protocol communication.

All MCP messages are wrapped in JSON-RPC 2.0 format for HTTP transport.
"""

from typing import Any, Optional, Union
from pydantic import BaseModel, Field


class JsonRpcRequest(BaseModel):
    """
    JSON-RPC 2.0 Request structure.

    Example:
        {
            "jsonrpc": "2.0",
            "method": "game_invitation",
            "params": { ... message payload ... },
            "id": 1
        }
    """

    jsonrpc: str = Field(default="2.0", frozen=True)
    method: str
    params: dict[str, Any] = Field(default_factory=dict)
    id: Optional[Union[int, str]] = None


class JsonRpcResponse(BaseModel):
    """
    JSON-RPC 2.0 Response structure.

    Example (success):
        {
            "jsonrpc": "2.0",
            "result": { ... response payload ... },
            "id": 1
        }

    Example (error):
        {
            "jsonrpc": "2.0",
            "error": {
                "code": -32600,
                "message": "Invalid Request"
            },
            "id": 1
        }
    """

    jsonrpc: str = Field(default="2.0", frozen=True)
    result: Optional[dict[str, Any]] = None
    error: Optional[dict[str, Any]] = None
    id: Optional[Union[int, str]] = None


class JsonRpcError(BaseModel):
    """
    JSON-RPC 2.0 Error object.

    Standard error codes:
    - -32700: Parse error
    - -32600: Invalid Request
    - -32601: Method not found
    - -32602: Invalid params
    - -32603: Internal error
    """

    code: int
    message: str
    data: Optional[Any] = None


def create_jsonrpc_request(
    method: str,
    params: dict[str, Any],
    request_id: Optional[Union[int, str]] = None,
) -> dict[str, Any]:
    """
    Create a JSON-RPC 2.0 request dictionary.

    Args:
        method: The method name (message_type in lowercase)
        params: The message payload
        request_id: Optional request ID for response matching

    Returns:
        Dictionary ready for JSON serialization
    """
    request = JsonRpcRequest(method=method, params=params, id=request_id)
    return request.model_dump(exclude_none=True)


def create_jsonrpc_response(
    result: Optional[dict[str, Any]] = None,
    error: Optional[JsonRpcError] = None,
    request_id: Optional[Union[int, str]] = None,
) -> dict[str, Any]:
    """
    Create a JSON-RPC 2.0 response dictionary.

    Args:
        result: Success response payload
        error: Error object (if request failed)
        request_id: Original request ID

    Returns:
        Dictionary ready for JSON serialization
    """
    response = JsonRpcResponse(
        result=result,
        error=error.model_dump() if error else None,
        id=request_id,
    )
    return response.model_dump(exclude_none=True)


def create_error_response(
    code: int,
    message: str,
    data: Optional[Any] = None,
    request_id: Optional[Union[int, str]] = None,
) -> dict[str, Any]:
    """
    Create a JSON-RPC 2.0 error response.

    Args:
        code: Error code
        message: Error message
        data: Additional error data
        request_id: Original request ID

    Returns:
        Dictionary ready for JSON serialization
    """
    error = JsonRpcError(code=code, message=message, data=data)
    return create_jsonrpc_response(error=error, request_id=request_id)
