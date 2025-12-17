"""
Unit tests for protocol models.

This module re-exports all protocol tests from split modules.
Run with: pytest tests/test_protocol.py -v
"""

# Re-export all tests from split modules for backwards compatibility
from .test_timestamp import TestUTCTimestampValidation
from .test_enums import TestParityChoice, TestGameResult, TestErrorCodes
from .test_helpers import TestHelperFunctions
from .test_messages import TestMessageEnvelope, TestRegistrationMessages, TestGameMessages

__all__ = [
    "TestUTCTimestampValidation",
    "TestParityChoice",
    "TestGameResult",
    "TestErrorCodes",
    "TestHelperFunctions",
    "TestMessageEnvelope",
    "TestRegistrationMessages",
    "TestGameMessages",
]
