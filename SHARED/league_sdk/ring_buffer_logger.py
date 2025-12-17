"""
Ring Buffer Logging System.

Provides a logging system that:
- Limits log file size (max lines per file)
- Limits number of log files (deletes oldest when exceeded)
- Shows status: file count, total lines, total KB

WHY Ring Buffer?
Logs can grow infinitely, filling up disk space. Ring buffer keeps
only the most recent logs, like a circular buffer that overwrites
the oldest data when full.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


# Configuration constants
DEFAULT_MAX_LINES = 1000      # Max lines before rotation
DEFAULT_MAX_FILES = 5         # Max log files to keep
DEFAULT_LOG_LEVEL = "INFO"    # Default logging level


class RingBufferHandler(logging.Handler):
    """
    A logging handler that implements ring buffer behavior.

    Features:
    - Creates new log file when max lines reached
    - Deletes oldest log file when max files reached
    - Tracks and displays logging statistics
    """

    def __init__(
        self,
        log_dir: Path,
        max_lines: int = DEFAULT_MAX_LINES,
        max_files: int = DEFAULT_MAX_FILES,
        filename_pattern: str = "app_{timestamp}.log",
    ):
        """
        Initialize the ring buffer handler.

        Args:
            log_dir: Directory to store log files
            max_lines: Maximum lines per log file before rotation
            max_files: Maximum number of log files to keep
            filename_pattern: Pattern for log filenames
        """
        super().__init__()

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.max_lines = max_lines
        self.max_files = max_files
        self.filename_pattern = filename_pattern

        self.current_file: Optional[Path] = None
        self.current_line_count = 0
        self.file_handle = None

        # Start new log file
        self._rotate_file()

    def _get_new_filename(self) -> str:
        """Generate new filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.filename_pattern.replace("{timestamp}", timestamp)

    def _rotate_file(self) -> None:
        """Create new log file and manage file count."""
        # Close current file if open
        if self.file_handle:
            self.file_handle.close()

        # Create new file
        new_filename = self._get_new_filename()
        self.current_file = self.log_dir / new_filename
        self.file_handle = open(self.current_file, 'w', encoding='utf-8')
        self.current_line_count = 0

        # Check and delete oldest files if exceeded
        self._cleanup_old_files()

    def _cleanup_old_files(self) -> None:
        """Delete oldest log files if max_files exceeded."""
        log_files = sorted(
            self.log_dir.glob("*.log"),
            key=lambda f: f.stat().st_mtime
        )

        while len(log_files) > self.max_files:
            oldest = log_files.pop(0)
            oldest.unlink()

    def emit(self, record: logging.LogRecord) -> None:
        """Write log record to file."""
        try:
            msg = self.format(record) + '\n'
            self.file_handle.write(msg)
            self.file_handle.flush()
            self.current_line_count += 1

            # Rotate if max lines reached
            if self.current_line_count >= self.max_lines:
                self._rotate_file()

        except Exception:
            self.handleError(record)

    def get_status(self) -> Dict[str, Any]:
        """Get current logging status."""
        log_files = list(self.log_dir.glob("*.log"))
        total_lines = 0
        total_size = 0

        for f in log_files:
            total_size += f.stat().st_size
            with open(f, 'r', encoding='utf-8') as file:
                total_lines += sum(1 for _ in file)

        return {
            'file_count': len(log_files),
            'total_lines': total_lines,
            'total_size_kb': round(total_size / 1024, 2),
            'max_lines_per_file': self.max_lines,
            'max_files': self.max_files,
            'current_file': str(self.current_file) if self.current_file else None,
            'current_lines': self.current_line_count,
        }

    def close(self) -> None:
        """Clean up resources."""
        if self.file_handle:
            self.file_handle.close()
        super().close()


def setup_ring_buffer_logger(
    name: str = "league",
    log_dir: Optional[Path] = None,
    max_lines: int = DEFAULT_MAX_LINES,
    max_files: int = DEFAULT_MAX_FILES,
    log_level: str = DEFAULT_LOG_LEVEL,
) -> logging.Logger:
    """
    Set up a logger with ring buffer handler.

    Args:
        name: Logger name
        log_dir: Directory for log files
        max_lines: Max lines per file
        max_files: Max number of files
        log_level: Logging level

    Returns:
        Configured logger instance
    """
    if log_dir is None:
        log_dir = Path(__file__).parent.parent / "logs"

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Add ring buffer handler
    handler = RingBufferHandler(
        log_dir=log_dir,
        max_lines=max_lines,
        max_files=max_files,
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    ))
    logger.addHandler(handler)

    return logger


def get_log_status(logger: logging.Logger) -> Optional[Dict[str, Any]]:
    """Get status from ring buffer handler if present."""
    for handler in logger.handlers:
        if isinstance(handler, RingBufferHandler):
            return handler.get_status()
    return None


def print_log_status(logger: logging.Logger) -> None:
    """Print current logging status."""
    status = get_log_status(logger)
    if status:
        print("\nLog Status:")
        print(f"  Files: {status['file_count']}/{status['max_files']}")
        print(f"  Total Lines: {status['total_lines']}")
        print(f"  Total Size: {status['total_size_kb']} KB")
        print(f"  Current File Lines: {status['current_lines']}")
