"""Application configuration utilities."""

from collections.abc import Mapping
import os
from typing import Any, Dict, Iterable, Optional

REQUIRED_ENV_VARS: tuple[str, ...] = (
    "SPOTIFY_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET",
    "APP_SECRET_KEY",
)


def _extract_from_source(source: Any, key: str) -> Optional[str]:
    """Return a configuration value from a mapping or object."""
    if source is None:
        return None

    if isinstance(source, Mapping):
        value = source.get(key)
        if value is not None:
            return str(value)
        return None

    # Fallback to attribute access for objects
    if hasattr(source, key):
        value = getattr(source, key)
        if value is not None:
            return str(value)
    return None


def validate_required_settings(source: Any = None, required: Iterable[str] = REQUIRED_ENV_VARS) -> Dict[str, str]:
    """Ensure required settings are available via configuration or environment.

    Parameters
    ----------
    source:
        Optional mapping/object containing configuration overrides.
    required:
        Iterable of setting names that must be available.

    Returns
    -------
    Dict[str, str]
        Mapping of validated configuration values.

    Raises
    ------
    RuntimeError
        If any required setting is missing.
    """

    resolved: Dict[str, str] = {}
    missing: list[str] = []

    for key in required:
        value = _extract_from_source(source, key)
        if value is None or value == "":
            value = os.getenv(key)
        if value is None or value == "":
            missing.append(key)
        else:
            resolved[key] = value

    if missing:
        formatted = ", ".join(missing)
        raise RuntimeError(
            "Missing required environment variables: "
            f"{formatted}. Ensure these values are configured before starting the app."
        )

    return resolved
