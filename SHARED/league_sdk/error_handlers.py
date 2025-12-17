"""
Error handling utilities for player agents.

Provides standardized error handlers for LEAGUE_ERROR and GAME_ERROR messages.
"""

import asyncio
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ErrorRecoveryAction(Enum):
    """Actions to take on error."""
    IGNORE = "ignore"
    LOG_ONLY = "log_only"
    RETRY = "retry"
    RE_REGISTER = "re_register"
    ABORT = "abort"


# Error code to recovery action mapping
ERROR_RECOVERY_MAP: Dict[str, ErrorRecoveryAction] = {
    # Retryable errors
    "E001": ErrorRecoveryAction.RETRY,      # TIMEOUT_ERROR
    "E009": ErrorRecoveryAction.RETRY,      # CONNECTION_ERROR
    "E010": ErrorRecoveryAction.RETRY,      # RATE_LIMITED

    # Auth errors - need re-registration
    "E011": ErrorRecoveryAction.RE_REGISTER,  # AUTH_TOKEN_MISSING
    "E012": ErrorRecoveryAction.RE_REGISTER,  # AUTH_TOKEN_INVALID

    # Non-retryable errors
    "E002": ErrorRecoveryAction.LOG_ONLY,   # INVALID_MESSAGE
    "E003": ErrorRecoveryAction.ABORT,      # PROTOCOL_MISMATCH
    "E004": ErrorRecoveryAction.LOG_ONLY,   # INVALID_PARITY_CHOICE
    "E005": ErrorRecoveryAction.RE_REGISTER,  # PLAYER_NOT_REGISTERED
    "E006": ErrorRecoveryAction.LOG_ONLY,   # MATCH_NOT_FOUND
    "E007": ErrorRecoveryAction.LOG_ONLY,   # OUT_OF_TURN
    "E008": ErrorRecoveryAction.LOG_ONLY,   # DEADLINE_PASSED
}


@dataclass
class ErrorContext:
    """Context information about an error."""
    error_code: str
    error_name: str
    error_description: str
    retryable: bool
    sender: str
    match_id: Optional[str] = None
    player_id: Optional[str] = None


def get_recovery_action(error_code: str) -> ErrorRecoveryAction:
    """Get recovery action for error code."""
    return ERROR_RECOVERY_MAP.get(error_code, ErrorRecoveryAction.LOG_ONLY)


class ErrorHandler:
    """
    Centralized error handler for player agents.

    Provides standardized handling of LEAGUE_ERROR and GAME_ERROR messages.
    """

    def __init__(
        self,
        logger: Any,
        on_re_register: Optional[Callable] = None,
        on_abort: Optional[Callable] = None,
    ):
        """
        Initialize error handler.

        Args:
            logger: Logger instance
            on_re_register: Callback for re-registration action
            on_abort: Callback for abort action
        """
        self.logger = logger
        self._on_re_register = on_re_register
        self._on_abort = on_abort
        self._error_counts: Dict[str, int] = {}

    def parse_error(self, params: Dict[str, Any]) -> ErrorContext:
        """Parse error message into ErrorContext."""
        return ErrorContext(
            error_code=params.get("error_code", "UNKNOWN"),
            error_name=params.get("error_name", "UNKNOWN_ERROR"),
            error_description=params.get("error_description", ""),
            retryable=params.get("retryable", False),
            sender=params.get("sender", "unknown"),
            match_id=params.get("match_id"),
            player_id=params.get("player_id"),
        )

    async def handle_league_error(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle LEAGUE_ERROR message.

        Args:
            params: Error message parameters

        Returns:
            Acknowledgment response
        """
        error = self.parse_error(params)
        self._record_error(error.error_code)

        self.logger.error(
            "LEAGUE_ERROR",
            f"{error.error_name}: {error.error_description}",
            error_code=error.error_code,
            retryable=error.retryable,
        )

        action = get_recovery_action(error.error_code)
        await self._execute_action(action, error)

        return {"status": "acknowledged", "error_code": error.error_code}

    async def handle_game_error(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle GAME_ERROR message.

        Args:
            params: Error message parameters

        Returns:
            Acknowledgment response
        """
        error = self.parse_error(params)
        self._record_error(error.error_code)

        self.logger.error(
            "GAME_ERROR",
            f"{error.error_name}: {error.error_description}",
            error_code=error.error_code,
            match_id=error.match_id,
            retryable=error.retryable,
        )

        action = get_recovery_action(error.error_code)
        await self._execute_action(action, error)

        return {"status": "acknowledged", "error_code": error.error_code}

    async def _execute_action(
        self,
        action: ErrorRecoveryAction,
        error: ErrorContext,
    ) -> None:
        """Execute recovery action."""
        if action == ErrorRecoveryAction.RE_REGISTER:
            if self._on_re_register:
                self.logger.info("RECOVERY", "Attempting re-registration")
                await self._on_re_register()

        elif action == ErrorRecoveryAction.ABORT:
            if self._on_abort:
                self.logger.warning("RECOVERY", "Aborting due to fatal error")
                await self._on_abort()

        elif action == ErrorRecoveryAction.RETRY:
            self.logger.info(
                "RECOVERY",
                f"Error is retryable, will retry on next request",
                error_code=error.error_code,
            )

    def _record_error(self, error_code: str) -> None:
        """Record error for statistics."""
        self._error_counts[error_code] = self._error_counts.get(error_code, 0) + 1

    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics."""
        return dict(self._error_counts)

    def reset_stats(self) -> None:
        """Reset error statistics."""
        self._error_counts.clear()
