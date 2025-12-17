"""
Resilience patterns for robust communication.

Implements:
- Retry with exponential backoff
- Circuit breaker (optional)
"""

import asyncio
import time
from typing import TypeVar, Callable, Any, Optional
from functools import wraps

T = TypeVar("T")


class RetryExhausted(Exception):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, attempts: int, last_error: Exception):
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(f"Retry exhausted after {attempts} attempts: {last_error}")


async def retry_with_backoff(
    func: Callable[..., Any],
    *args,
    max_retries: int = 3,
    backoff_seconds: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
    **kwargs,
) -> Any:
    """
    Execute a function with retry and exponential backoff.

    Args:
        func: Async function to execute
        *args: Positional arguments for func
        max_retries: Maximum number of retry attempts
        backoff_seconds: Base wait time between retries
        retryable_exceptions: Tuple of exceptions that trigger retry
        **kwargs: Keyword arguments for func

    Returns:
        Result of successful function call

    Raises:
        RetryExhausted: If all retries fail
    """
    last_error: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except retryable_exceptions as e:
            last_error = e

            if attempt < max_retries:
                # Exponential backoff: 2s, 4s, 8s...
                wait_time = backoff_seconds * (2 ** attempt)
                await asyncio.sleep(wait_time)
            else:
                raise RetryExhausted(attempt + 1, e)

    # Should never reach here, but just in case
    raise RetryExhausted(max_retries + 1, last_error or Exception("Unknown error"))


def sync_retry_with_backoff(
    func: Callable[..., T],
    *args,
    max_retries: int = 3,
    backoff_seconds: float = 2.0,
    retryable_exceptions: tuple = (Exception,),
    **kwargs,
) -> T:
    """
    Synchronous version of retry with backoff.

    Args:
        func: Function to execute
        *args: Positional arguments for func
        max_retries: Maximum number of retry attempts
        backoff_seconds: Base wait time between retries
        retryable_exceptions: Tuple of exceptions that trigger retry
        **kwargs: Keyword arguments for func

    Returns:
        Result of successful function call

    Raises:
        RetryExhausted: If all retries fail
    """
    last_error: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retryable_exceptions as e:
            last_error = e

            if attempt < max_retries:
                wait_time = backoff_seconds * (2 ** attempt)
                time.sleep(wait_time)
            else:
                raise RetryExhausted(attempt + 1, e)

    raise RetryExhausted(max_retries + 1, last_error or Exception("Unknown error"))


class CircuitBreaker:
    """
    Simple circuit breaker to prevent cascading failures.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failing fast, requests rejected immediately
    - HALF_OPEN: Testing if service recovered
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 30.0,
    ):
        """
        Initialize the circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            reset_timeout: Seconds to wait before trying again
        """
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout

        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._state = "CLOSED"

    @property
    def state(self) -> str:
        """Get current circuit state."""
        if self._state == "OPEN":
            # Check if we should try again
            if (
                self._last_failure_time
                and time.time() - self._last_failure_time > self.reset_timeout
            ):
                self._state = "HALF_OPEN"
        return self._state

    def record_success(self) -> None:
        """Record a successful call."""
        self._failure_count = 0
        self._state = "CLOSED"

    def record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._failure_count >= self.failure_threshold:
            self._state = "OPEN"

    def is_open(self) -> bool:
        """Check if circuit is open (rejecting calls)."""
        return self.state == "OPEN"

    def can_execute(self) -> bool:
        """Check if a call can be attempted."""
        return self.state in ("CLOSED", "HALF_OPEN")
