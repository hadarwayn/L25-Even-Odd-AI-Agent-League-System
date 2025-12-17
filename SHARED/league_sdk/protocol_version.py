"""
Protocol version validation utilities.

Provides version checking and compatibility validation
for the league.v2 protocol.
"""

import re
from typing import Tuple, Optional
from dataclasses import dataclass


# Current protocol version
PROTOCOL_VERSION = "2.1.0"
PROTOCOL_NAME = "league.v2"

# Minimum compatible version
MIN_COMPATIBLE_VERSION = "2.0.0"


@dataclass
class VersionInfo:
    """Parsed version information."""
    major: int
    minor: int
    patch: int
    raw: str

    def __str__(self) -> str:
        return self.raw

    def to_tuple(self) -> Tuple[int, int, int]:
        return (self.major, self.minor, self.patch)


def parse_version(version_str: str) -> Optional[VersionInfo]:
    """
    Parse version string into VersionInfo.

    Args:
        version_str: Version string (e.g., "2.1.0")

    Returns:
        VersionInfo or None if invalid
    """
    pattern = r"^(\d+)\.(\d+)\.(\d+)$"
    match = re.match(pattern, version_str)

    if not match:
        return None

    return VersionInfo(
        major=int(match.group(1)),
        minor=int(match.group(2)),
        patch=int(match.group(3)),
        raw=version_str,
    )


def is_compatible(version_str: str) -> bool:
    """
    Check if a version is compatible with current protocol.

    Compatibility rules:
    - Major version must match
    - Minor version must be >= minimum
    - Patch version is ignored

    Args:
        version_str: Version string to check

    Returns:
        True if compatible
    """
    version = parse_version(version_str)
    if not version:
        return False

    current = parse_version(PROTOCOL_VERSION)
    minimum = parse_version(MIN_COMPATIBLE_VERSION)

    if not current or not minimum:
        return False

    # Major version must match
    if version.major != current.major:
        return False

    # Must be >= minimum version
    return version.to_tuple() >= minimum.to_tuple()


def get_version_mismatch_error(version_str: str) -> Optional[str]:
    """
    Get error message for version mismatch.

    Args:
        version_str: Version string that was received

    Returns:
        Error message or None if compatible
    """
    if is_compatible(version_str):
        return None

    version = parse_version(version_str)
    if not version:
        return f"Invalid version format: {version_str}"

    current = parse_version(PROTOCOL_VERSION)

    if version.major != current.major:
        return (
            f"Major version mismatch: got {version.major}, "
            f"expected {current.major}"
        )

    return (
        f"Version {version_str} is below minimum "
        f"compatible version {MIN_COMPATIBLE_VERSION}"
    )


def validate_protocol_header(protocol: str, version: Optional[str] = None) -> bool:
    """
    Validate protocol header from message.

    Args:
        protocol: Protocol identifier (e.g., "league.v2")
        version: Optional version string

    Returns:
        True if valid
    """
    if protocol != PROTOCOL_NAME:
        return False

    if version and not is_compatible(version):
        return False

    return True


def create_version_metadata() -> dict:
    """
    Create version metadata for registration messages.

    Returns:
        Dictionary with version info
    """
    return {
        "protocol_version": PROTOCOL_VERSION,
        "min_compatible_version": MIN_COMPATIBLE_VERSION,
        "protocol": PROTOCOL_NAME,
    }


def check_agent_compatibility(agent_meta: dict) -> Tuple[bool, str]:
    """
    Check if an agent's version is compatible.

    Args:
        agent_meta: Agent metadata containing version info

    Returns:
        Tuple of (is_compatible, message)
    """
    version = agent_meta.get("protocol_version")

    if not version:
        return True, "No version specified, assuming compatible"

    if is_compatible(version):
        return True, f"Version {version} is compatible"

    error = get_version_mismatch_error(version)
    return False, error or "Unknown version error"
