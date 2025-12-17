"""
JSONL structured logging for the league system.

Writes JSON Lines format logs with event tracking.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Optional


class JsonLogger:
    """JSON Lines structured logger."""

    def __init__(
        self,
        agent_type: str,
        agent_id: str,
        log_dir: Optional[str] = None,
    ):
        """
        Initialize logger.

        Args:
            agent_type: Type of agent (league_manager, referee, player)
            agent_id: Agent identifier
            log_dir: Log directory. Defaults to SHARED/logs/{agent_type}/
        """
        self.agent_type = agent_type
        self.agent_id = agent_id

        if log_dir:
            self._log_dir = Path(log_dir)
        else:
            sdk_dir = Path(__file__).parent
            self._log_dir = sdk_dir.parent / "logs" / agent_type

        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self._log_dir / f"{agent_id}.log.jsonl"

    def _write(self, record: dict[str, Any]) -> None:
        """Write a log record to file."""
        try:
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, default=str) + "\n")
        except IOError as e:
            # Don't crash the agent on log failure
            print(f"Log write error: {e}", file=sys.stderr)

    def _create_record(
        self,
        level: str,
        event_type: str,
        message: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create a log record."""
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "agent_type": self.agent_type,
            "agent_id": self.agent_id,
            "event_type": event_type,
            "message": message,
            **kwargs,
        }

    def info(self, event_type: str, message: str, **kwargs: Any) -> None:
        """Log info level message."""
        record = self._create_record("INFO", event_type, message, **kwargs)
        self._write(record)

    def warning(self, event_type: str, message: str, **kwargs: Any) -> None:
        """Log warning level message."""
        record = self._create_record("WARNING", event_type, message, **kwargs)
        self._write(record)

    def error(self, event_type: str, message: str, **kwargs: Any) -> None:
        """Log error level message."""
        record = self._create_record("ERROR", event_type, message, **kwargs)
        self._write(record)

    def debug(self, event_type: str, message: str, **kwargs: Any) -> None:
        """Log debug level message."""
        record = self._create_record("DEBUG", event_type, message, **kwargs)
        self._write(record)

    def message_sent(self, message_type: str, recipient: str, **kwargs: Any) -> None:
        """Log outgoing message."""
        self.info(
            "MESSAGE_SENT",
            f"Sent {message_type} to {recipient}",
            message_type=message_type,
            recipient=recipient,
            **kwargs,
        )

    def message_received(self, message_type: str, sender: str, **kwargs: Any) -> None:
        """Log incoming message."""
        self.info(
            "MESSAGE_RECEIVED",
            f"Received {message_type} from {sender}",
            message_type=message_type,
            sender=sender,
            **kwargs,
        )

    def match_event(self, match_id: str, event: str, **kwargs: Any) -> None:
        """Log match-related event."""
        self.info("MATCH_EVENT", event, match_id=match_id, **kwargs)
