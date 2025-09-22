"""
Simple retry/backoff utilities for Spotify API calls.
"""

import time
from typing import Callable, Any

try:
    # Prefer Spotipy exception for HTTP status access
    from spotipy.exceptions import SpotifyException  # type: ignore
except Exception:  # pragma: no cover - fallback if spotipy changes
    SpotifyException = Exception  # type: ignore


class RetryConfig:
    def __init__(
        self,
        retries: int = 5,
        base_delay: float = 0.5,
        max_delay: float = 10.0,
        retry_on: tuple = (429, 500, 502, 503, 504),
    ) -> None:
        self.retries = retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.retry_on = retry_on


def _sleep_with_jitter(delay: float) -> None:
    # Minimal jitter to avoid thundering herd; avoid importing random.
    time.sleep(delay)


def retry_request(func: Callable[..., Any], *, config: RetryConfig = RetryConfig()) -> Callable[..., Any]:
    """
    Decorator-like wrapper for functions that make HTTP requests via Spotipy/requests.
    Expects functions to raise requests.HTTPError or return objects with 'status'/'headers' on error.
    """

    def wrapper(*args, **kwargs):
        delay = config.base_delay
        attempt = 0
        while True:
            try:
                return func(*args, **kwargs)
            except SpotifyException as e:  # Spotipy errors
                # SpotipyException exposes http_status and headers
                status = getattr(e, 'http_status', None)
                headers = getattr(e, 'headers', {}) or {}
                if status in config.retry_on and attempt < config.retries:
                    # Respect Retry-After if present
                    ra = headers.get('Retry-After') or headers.get('retry-after')
                    retry_after = 0
                    try:
                        retry_after = float(ra) if ra is not None else 0
                    except Exception:
                        retry_after = 0
                    wait = max(delay, retry_after)
                    _sleep_with_jitter(min(wait, config.max_delay))
                    delay = min(delay * 2, config.max_delay)
                    attempt += 1
                    continue
                raise
            except Exception:
                # Generic connection/transport error path
                if attempt < config.retries:
                    _sleep_with_jitter(delay)
                    delay = min(delay * 2, config.max_delay)
                    attempt += 1
                    continue
                raise

    return wrapper
