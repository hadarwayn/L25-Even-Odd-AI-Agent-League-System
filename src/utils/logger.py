"""
JSON Lines logger for the Player Agent.

Writes structured logs in JSONL format for easy parsing and analysis.
Each log entry is a single JSON object on one line.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


class JsonLogger:
    """
    Logger that writes JSON Lines format logs.

    Each log entry includes:
    - timestamp (UTC)
    - level
    - event_type
    - message
    - Additional context fields
    """

    def __init__(
        self,
        player_id: str,
        log_dir: str = "logs/agents",
        level: str = "INFO",
    ):
        """
        Initialize the JSON logger.

        Args:
            player_id: Player identifier for the log file name
            log_dir: Directory to write log files
            level: Minimum log level (DEBUG, INFO, WARNING, ERROR)
        """
        self.player_id = player_id
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.log_dir / f"{player_id}.log.jsonl"
        self.level = getattr(logging, level.upper(), logging.INFO)

        # Also set up standard logging for console output
        self._setup_console_logger()

    def _setup_console_logger(self) -> None:
        """Set up console logging for debugging."""
        self.console_logger = logging.getLogger(f"player.{self.player_id}")
        self.console_logger.setLevel(self.level)

        if not self.console_logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(
                logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
            )
            self.console_logger.addHandler(handler)

    def _get_timestamp(self) -> str:
        """Get current UTC timestamp."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _write_log(
        self,
        level: str,
        event_type: str,
        message: str,
        **kwargs: Any,
    ) -> None:
        """Write a log entry to the JSONL file."""
        entry = {
            "timestamp": self._get_timestamp(),
            "level": level,
            "player_id": self.player_id,
            "event_type": event_type,
            "message": message,
            **kwargs,
        }

        # Sanitize auth_token if present (only log first 8 chars)
        if "auth_token" in entry and entry["auth_token"]:
            token = entry["auth_token"]
            entry["auth_token"] = f"{token[:8]}..." if len(token) > 8 else "***"

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except IOError:
            # Don't crash the agent if logging fails
            pass

    def debug(self, event_type: str, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        if self.level <= logging.DEBUG:
            self._write_log("DEBUG", event_type, message, **kwargs)
            self.console_logger.debug(f"[{event_type}] {message}")

    def info(self, event_type: str, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        if self.level <= logging.INFO:
            self._write_log("INFO", event_type, message, **kwargs)
            self.console_logger.info(f"[{event_type}] {message}")

    def warning(self, event_type: str, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        if self.level <= logging.WARNING:
            self._write_log("WARNING", event_type, message, **kwargs)
            self.console_logger.warning(f"[{event_type}] {message}")

    def error(self, event_type: str, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        if self.level <= logging.ERROR:
            self._write_log("ERROR", event_type, message, **kwargs)
            self.console_logger.error(f"[{event_type}] {message}")

    def log_message_received(
        self,
        message_type: str,
        sender: str,
        match_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Log a received protocol message."""
        self.info(
            "MESSAGE_RECEIVED",
            f"Received {message_type} from {sender}",
            message_type=message_type,
            sender=sender,
            match_id=match_id,
            **kwargs,
        )

    def log_message_sent(
        self,
        message_type: str,
        recipient: str,
        match_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Log a sent protocol message."""
        self.info(
            "MESSAGE_SENT",
            f"Sent {message_type} to {recipient}",
            message_type=message_type,
            recipient=recipient,
            match_id=match_id,
            **kwargs,
        )

    def log_game_result(
        self,
        match_id: str,
        result: str,
        choice: str,
        drawn_number: int,
        opponent_id: str,
    ) -> None:
        """Log a game result."""
        self.info(
            "GAME_RESULT",
            f"Match {match_id}: {result} (chose {choice}, number was {drawn_number})",
            match_id=match_id,
            result=result,
            choice=choice,
            drawn_number=drawn_number,
            opponent_id=opponent_id,
        )


def setup_logger(
    player_id: str,
    log_dir: str = "logs/agents",
    level: str = "INFO",
) -> JsonLogger:
    """
    Create and configure a JSON logger for a player.

    Args:
        player_id: Player identifier
        log_dir: Directory for log files
        level: Minimum log level

    Returns:
        Configured JsonLogger instance
    """
    return JsonLogger(player_id=player_id, log_dir=log_dir, level=level)
