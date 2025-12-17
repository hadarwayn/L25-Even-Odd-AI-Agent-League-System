"""
Circuit breaker pattern implementation.

Prevents cascading failures by temporarily blocking requests
to failing services.
"""

import time
import asyncio
from enum import Enum
from typing import Optional, Callable, Any
from dataclasses import dataclass, field
from functools import wraps


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"      # Normal operation, requests flow through
    OPEN = "OPEN"          # Failing, requests blocked
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered


# Configuration constants
DEFAULT_FAILURE_THRESHOLD = 5  # Failures before opening circuit
DEFAULT_SUCCESS_THRESHOLD = 2  # Successes to close circuit
DEFAULT_TIMEOUT_SECONDS = 60   # Time before half-open transition


@dataclass
class CircuitBreaker:
    """
    Circuit breaker for fault tolerance.

    Implements the circuit breaker pattern to prevent cascading failures
    when a service is unavailable or slow.

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service failing, requests fail fast
    - HALF_OPEN: Testing service recovery with limited requests
    """

    failure_threshold: int = DEFAULT_FAILURE_THRESHOLD
    success_threshold: int = DEFAULT_SUCCESS_THRESHOLD
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    _state: CircuitState = field(default=CircuitState.CLOSED)
    _failure_count: int = field(default=0)
    _success_count: int = field(default=0)
    _last_failure_time: Optional[float] = field(default=None)
    _last_state_change: float = field(default_factory=time.time)

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for timeout transition."""
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self.timeout_seconds:
                self._transition_to(CircuitState.HALF_OPEN)
        return self._state

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state."""
        self._state = new_state
        self._last_state_change = time.time()

        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
            self._success_count = 0
        elif new_state == CircuitState.HALF_OPEN:
            self._success_count = 0

    def record_success(self) -> None:
        """Record a successful call."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.success_threshold:
                self._transition_to(CircuitState.CLOSED)
        elif self._state == CircuitState.CLOSED:
            self._failure_count = 0  # Reset on success

    def record_failure(self) -> None:
        """Record a failed call."""
        self._failure_count += 1
        self._last_failure_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._transition_to(CircuitState.OPEN)
        elif self._state == CircuitState.CLOSED:
            if self._failure_count >= self.failure_threshold:
                self._transition_to(CircuitState.OPEN)

    def can_execute(self) -> bool:
        """Check if a call can be executed."""
        state = self.state  # This triggers timeout check
        return state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)

    def get_status(self) -> dict:
        """Get circuit breaker status for monitoring."""
        return {
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "last_failure": self._last_failure_time,
            "last_state_change": self._last_state_change,
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit is open."""
    pass


def with_circuit_breaker(circuit: CircuitBreaker):
    """
    Decorator to wrap async function with circuit breaker.

    Usage:
        circuit = CircuitBreaker()

        @with_circuit_breaker(circuit)
        async def call_service():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not circuit.can_execute():
                raise CircuitBreakerOpen(
                    f"Circuit open, retry after {circuit.timeout_seconds}s"
                )

            try:
                result = await func(*args, **kwargs)
                circuit.record_success()
                return result
            except Exception as e:
                circuit.record_failure()
                raise

        return wrapper
    return decorator


class CircuitBreakerRegistry:
    """
    Registry for managing multiple circuit breakers.

    Maintains separate circuit breakers for different endpoints.
    """

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}

    def get(
        self,
        endpoint: str,
        failure_threshold: int = DEFAULT_FAILURE_THRESHOLD,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    ) -> CircuitBreaker:
        """Get or create circuit breaker for endpoint."""
        if endpoint not in self._breakers:
            self._breakers[endpoint] = CircuitBreaker(
                failure_threshold=failure_threshold,
                timeout_seconds=timeout_seconds,
            )
        return self._breakers[endpoint]

    def get_all_status(self) -> dict[str, dict]:
        """Get status of all circuit breakers."""
        return {
            endpoint: breaker.get_status()
            for endpoint, breaker in self._breakers.items()
        }
